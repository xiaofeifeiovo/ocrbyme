"""OCR 客户端模块 - 封装 Qwen3-VL-Flash API 调用"""

import base64
import logging
from pathlib import Path
from typing import Any

from openai import OpenAI
from PIL import Image

from ocrbyme.config import get_settings
from ocrbyme.models.types import APIError, RateLimitError
from ocrbyme.utils.retry import retry_on_error

logger = logging.getLogger(__name__)


class QwenVLClient:
    """Qwen3-VL-Flash API 客户端

    封装 Qwen3-VL-Flash API 调用逻辑,提供简洁的 OCR 接口。
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = 60,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """初始化 OCR 客户端

        Args:
            api_key: API Key (None 则从环境变量读取)
            base_url: API 端点 (None 则使用默认值)
            model: 模型名称 (None 则使用默认值)
            timeout: 请求超时 (秒)
            temperature: 温度参数 (0.0-2.0, 默认 0.0)
            max_tokens: 最大输出 token 数

        Raises:
            APIError: 初始化失败
        """
        # 从配置读取默认值
        settings = get_settings()

        self.api_key = api_key or settings.dashscope_api_key
        self.base_url = base_url or settings.api_base_url
        self.model = model or settings.model_name
        self.timeout = timeout
        self.high_resolution = settings.high_resolution
        self.temperature = temperature if temperature is not None else settings.temperature
        self.max_tokens = max_tokens if max_tokens is not None else settings.max_tokens

        # 初始化 OpenAI 客户端
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=timeout,
            )
            logger.info(
                f"OCR 客户端初始化成功: model={self.model}, "
                f"base_url={self.base_url}, timeout={timeout}s"
            )
        except Exception as e:
            raise APIError(f"OCR 客户端初始化失败: {e}") from e

    def _encode_image_to_base64(self, image_path: Path) -> str:
        """将图像编码为 base64 data URL

        Args:
            image_path: 图像路径

        Returns:
            base64 data URL 字符串
        """
        # 打开图像并获取格式
        with Image.open(image_path) as img:
            # 获取图像格式
            img_format = img.format or "PNG"
            if img_format == "JPEG":
                mime_type = "jpeg"
            elif img_format == "PNG":
                mime_type = "png"
            else:
                mime_type = "png"

            # 保存到内存中的字节流
            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format=img_format)
            buffer.seek(0)

            # 编码为 base64
            image_data = base64.b64encode(buffer.read()).decode("utf-8")

            # 构建 data URL
            return f"data:image/{mime_type};base64,{image_data}"

    @retry_on_error(
        max_attempts=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(APIError, RateLimitError),
    )
    def ocr_image(
        self,
        image_path: Path | str,
        prompt: str = "qwenvl markdown",
    ) -> str:
        """对单张图像进行 OCR,返回 Markdown 文本

        Args:
            image_path: 图像路径
            prompt: 提示词 (默认触发 markdown 模式)

        Returns:
            识别后的 Markdown 文本

        Raises:
            APIError: API 调用失败
            RateLimitError: 速率限制
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise APIError(f"图像文件不存在: {image_path}")

        logger.debug(f"开始 OCR: {image_path.name}")

        # 将图像编码为 base64
        base64_url = self._encode_image_to_base64(image_path)

        try:
            # 构建请求参数
            request_params: dict[str, Any] = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": base64_url},
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
                "extra_body": {
                    "vl_high_resolution_images": self.high_resolution
                },
            }

            # 添加温度参数 (提高稳定性)
            if self.temperature is not None:
                request_params["temperature"] = self.temperature

            # 添加 max_tokens 参数
            if self.max_tokens is not None:
                request_params["max_tokens"] = self.max_tokens

            # 调用 API
            response = self.client.chat.completions.create(**request_params)

            # 提取结果
            markdown_text = response.choices[0].message.content

            if not markdown_text:
                raise APIError("API 返回空内容")

            logger.debug(f"OCR 完成: {len(markdown_text)} 字符")
            return markdown_text

        except Exception as e:
            # 处理特定错误
            error_str = str(e)

            # 速率限制 (HTTP 429)
            if "429" in error_str or "rate" in error_str.lower():
                raise RateLimitError(
                    f"API 速率限制: {e}",
                    retry_after=5,
                ) from e

            # 认证失败 (HTTP 401)
            if "401" in error_str or "auth" in error_str.lower():
                raise APIError(
                    f"API 认证失败,请检查 API Key: {e}",
                    status_code=401,
                ) from e

            # 其他 API 错误
            raise APIError(f"API 调用失败: {e}") from e

    def ocr_images_batch(
        self,
        image_paths: list[Path | str],
        prompt: str = "qwenvl markdown",
    ) -> list[str]:
        """批量 OCR 多张图像

        Args:
            image_paths: 图像路径列表
            prompt: 提示词

        Returns:
            Markdown 文本列表,与输入顺序一致

        Raises:
            APIError: API 调用失败
        """
        results = []

        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"OCR 进度: {i}/{len(image_paths)}")

            try:
                markdown = self.ocr_image(image_path, prompt)
                results.append(markdown)
            except Exception as e:
                logger.error(f"第 {i} 张图像 OCR 失败: {e}")
                # 失败时添加错误注释
                results.append(f"<!-- OCR 失败: {e} -->")

        return results

    def close(self) -> None:
        """关闭客户端"""
        try:
            self.client.close()
            logger.info("OCR 客户端已关闭")
        except Exception as e:
            logger.warning(f"关闭 OCR 客户端失败: {e}")

    def __enter__(self) -> "QwenVLClient":
        """上下文管理器入口"""
        return self

    def __exit__(self, *args: Any) -> None:
        """上下文管理器退出"""
        self.close()
