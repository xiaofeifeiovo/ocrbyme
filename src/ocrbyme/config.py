"""配置管理模块"""

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from ocrbyme.models.types import ConfigurationError


class Settings(BaseSettings):
    """应用配置

    从环境变量和 .env 文件读取配置。
    优先级: 环境变量 > .env 文件 > 默认值
    """

    # API 配置
    dashscope_api_key: str
    api_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model_name: str = "qwen3-vl-flash"

    # PDF 处理配置
    default_dpi: int = 200
    default_output_format: str = "PNG"

    # OCR 配置
    default_prompt: str = "qwenvl markdown"
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0

    # 高分辨率模式 (提升识别精度)
    high_resolution: bool = True

    # 输出配置
    extract_images: bool = True
    image_subdir: str = "images"

    # 模型配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OCRBYME_",
        case_sensitive=False,
        extra="ignore",
    )

    def validate(self) -> None:
        """验证配置

        Raises:
            ConfigurationError: 配置无效
        """
        if not self.dashscope_api_key or self.dashscope_api_key == "your_api_key_here":
            raise ConfigurationError(
                "DASHSCOPE_API_KEY 未设置。"
                "请在 .env 文件中设置 DASHSCOPE_API_KEY 或设置环境变量。"
            )

        if self.default_dpi < 72 or self.default_dpi > 600:
            raise ConfigurationError(
                f"DPI 设置无效: {self.default_dpi}。"
                "DPI 应在 72 到 600 之间。"
            )

        if self.timeout < 1 or self.timeout > 600:
            raise ConfigurationError(
                f"超时设置无效: {self.timeout}。"
                "超时应在 1 到 600 秒之间。"
            )


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例

    Returns:
        Settings: 配置对象

    Raises:
        ConfigurationError: 配置无效
    """
    # 尝试从环境变量读取 DASHSCOPE_API_KEY
    # 如果环境变量中没有,使用 OCRBYME_DASHSCOPE_API_KEY
    env_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OCRBYME_DASHSCOPE_API_KEY", "")

    # 创建配置对象
    settings = Settings(
        dashscope_api_key=env_key,
    )

    # 验证配置
    settings.validate()

    return settings


def reset_settings() -> None:
    """重置配置缓存 (主要用于测试)"""
    get_settings.cache_clear()
