"""OCRByMe - PDF to Markdown OCR Tool

使用 Qwen3-VL-Flash API 将 PDF 转换为 Markdown 文件。
"""

__version__ = "0.1.0"
__author__ = "xiaofeifei"
__license__ = "MIT"

from ocrbyme.models.types import (
    OCRByMeError,
    PDFProcessingError,
    APIError,
    RateLimitError,
    ConfigurationError,
)

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "OCRByMeError",
    "PDFProcessingError",
    "APIError",
    "RateLimitError",
    "ConfigurationError",
]
