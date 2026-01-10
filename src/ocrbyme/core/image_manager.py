"""图片管理器模块 - 提取和保存图片"""

import base64
import logging
import re
from pathlib import Path
from typing import Any

from ocrbyme.models.types import OCRByMeError

logger = logging.getLogger(__name__)


class ImageExtractionError(OCRByMeError):
    """图片提取错误"""
    pass


class ImageManager:
    """图片提取和管理

    从 OCR 结果中提取 base64 图片并保存到文件系统。
    """

    # 匹配 data URL 格式的图片
    # 例如: ![alt](data:image/png;base64,iVBORw0KG...)
    DATA_URL_PATTERN = re.compile(
        r'!\[(.*?)\]\(data:image/(\w+);base64,([A-Za-z0-9+/=]+)\)'
    )

    def __init__(self, output_dir: Path, image_subdir: str = "images") -> None:
        """初始化图片管理器

        Args:
            output_dir: 输出目录
            image_subdir: 图片子目录名称
        """
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / image_subdir
        self.images_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"图片管理器初始化: 图片目录={self.images_dir}")

    def extract_and_save_images(
        self,
        markdown: str,
        page_num: int,
    ) -> tuple[str, list[Path]]:
        """从 Markdown 中提取图片并保存

        Args:
            markdown: Markdown 文本
            page_num: 页码

        Returns:
            (处理后的 Markdown, 保存的图片路径列表)

        Raises:
            ImageExtractionError: 图片提取失败
        """
        saved_images = []
        processed_markdown = markdown
        offset = 0

        # 查找所有 data URL 格式的图片
        for match in self.DATA_URL_PATTERN.finditer(markdown):
            try:
                alt_text = match.group(1)
                image_format = match.group(2)
                base64_data = match.group(3)

                # 解码 base64 数据
                image_data = base64.b64decode(base64_data)

                # 生成图片文件名
                image_index = len(saved_images) + 1
                image_filename = f"page_{page_num}_img_{image_index}.{image_format}"
                image_path = self.images_dir / image_filename

                # 保存图片
                image_path.write_bytes(image_data)
                logger.debug(f"保存图片: {image_path}")
                saved_images.append(image_path)

                # 替换 Markdown 中的 data URL 为相对路径
                # 注意: 由于我们要在原字符串中替换,需要考虑位置偏移
                relative_path = f"{self.images_dir.name}/{image_filename}"
                replacement = f'![{alt_text}]({relative_path})'

                # 计算替换位置
                start, end = match.span()
                # 更新偏移量 (每次替换后,原文本长度会变化)
                adjusted_start = start + offset
                adjusted_end = end + offset

                # 替换
                processed_markdown = (
                    processed_markdown[:adjusted_start]
                    + replacement
                    + processed_markdown[adjusted_end:]
                )

                # 更新偏移量
                offset += len(replacement) - (end - start)

            except Exception as e:
                logger.warning(f"提取图片失败: {e}")
                # 继续处理其他图片
                continue

        logger.info(f"页码 {page_num}: 提取 {len(saved_images)} 张图片")
        return processed_markdown, saved_images

    def extract_and_save_images_from_markdown_list(
        self,
        markdown_list: list[str],
    ) -> tuple[list[str], list[Path]]:
        """从 Markdown 列表中批量提取图片

        Args:
            markdown_list: Markdown 文本列表 (每页一个)

        Returns:
            (处理后的 Markdown 列表, 所有保存的图片路径列表)
        """
        processed_list = []
        all_images = []

        for page_num, markdown in enumerate(markdown_list, 1):
            processed, images = self.extract_and_save_images(markdown, page_num)
            processed_list.append(processed)
            all_images.extend(images)

        return processed_list, all_images

    @staticmethod
    def decode_base64_image(data_url: str) -> tuple[bytes, str]:
        """解码 data URL 格式的图片

        Args:
            data_url: data URL 字符串
                例如: data:image/png;base64,iVBORw0KG...

        Returns:
            (图片二进制数据, 格式)

        Raises:
            ImageExtractionError: 解码失败
        """
        try:
            # 解析 data URL
            # 格式: data:image/<format>;base64,<data>
            if not data_url.startswith("data:image/"):
                raise ImageExtractionError(f"无效的 data URL: {data_url[:50]}...")

            # 提取格式和数据
            parts = data_url.split(";base64,")
            if len(parts) != 2:
                raise ImageExtractionError(f"无效的 data URL 格式: {data_url[:50]}...")

            # 提取图片格式
            format_part = parts[0].replace("data:image/", "")
            image_format = format_part

            # 解码 base64
            base64_data = parts[1]
            image_data = base64.b64decode(base64_data)

            return image_data, image_format

        except Exception as e:
            raise ImageExtractionError(f"解码 base64 图片失败: {e}") from e

    def generate_image_name(
        self,
        page_num: int,
        img_index: int,
        format: str = "png",
    ) -> str:
        """生成图片文件名

        Args:
            page_num: 页码
            img_index: 图片索引 (从 1 开始)
            format: 图片格式

        Returns:
            图片文件名: page_{page_num}_img_{img_index}.{format}
        """
        return f"page_{page_num}_img_{img_index}.{format}"
