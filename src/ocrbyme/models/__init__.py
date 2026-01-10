"""数据模型包"""

from ocrbyme.models.types import (
    APIError,
    ConfigurationError,
    OCRByMeError,
    PDFProcessingError,
    ProcessingResult,
    RateLimitError,
)

__all__ = [
    "OCRByMeError",
    "PDFProcessingError",
    "APIError",
    "RateLimitError",
    "ConfigurationError",
    "ProcessingResult",
]
