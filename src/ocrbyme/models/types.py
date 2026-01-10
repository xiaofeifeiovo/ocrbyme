"""数据模型和自定义异常"""

from pathlib import Path
from typing import Any


# ==================== 自定义异常 ====================


class OCRByMeError(Exception):
    """OCRByMe 基础异常"""

    def __init__(self, message: str, *args: Any) -> None:
        self.message = message
        super().__init__(message, *args)


class PDFProcessingError(OCRByMeError):
    """PDF 处理错误"""

    pass


class APIError(OCRByMeError):
    """API 调用错误"""

    def __init__(self, message: str, status_code: int | None = None, *args: Any) -> None:
        self.status_code = status_code
        super().__init__(message, *args)


class RateLimitError(APIError):
    """速率限制错误"""

    def __init__(self, message: str = "API 速率限制", retry_after: int | None = None) -> None:
        self.retry_after = retry_after
        super().__init__(message, status_code=429)


class ConfigurationError(OCRByMeError):
    """配置错误"""

    pass


# ==================== 数据模型 ====================


class ProcessingResult:
    """处理结果数据模型"""

    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        page_count: int,
        images_extracted: int,
        processing_time: float,
    ) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.page_count = page_count
        self.images_extracted = images_extracted
        self.processing_time = processing_time

    def __repr__(self) -> str:
        return (
            f"ProcessingResult("
            f"input={self.input_path.name}, "
            f"output={self.output_path.name}, "
            f"pages={self.page_count}, "
            f"images={self.images_extracted}, "
            f"time={self.processing_time:.2f}s)"
        )
