"""重试机制装饰器"""

import logging
import time
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from ocrbyme.models.types import APIError, RateLimitError

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """指数退避重试装饰器

    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟(秒)
        backoff: 退避系数(每次重试延迟时间乘以这个系数)
        exceptions: 需要重试的异常类型

    Returns:
        装饰器函数

    Example:
        @retry_on_error(max_attempts=3, delay=1.0, exceptions=(APIError,))
        def api_call():
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    # 最后一次尝试失败,抛出异常
                    if attempt == max_attempts - 1:
                        logger.error(f"重试 {max_attempts} 次后仍然失败: {e}")
                        raise

                    # 速率限制错误,使用 retry-after 指定的延迟
                    if isinstance(e, RateLimitError) and e.retry_after:
                        current_delay = e.retry_after
                        logger.warning(
                            f"触发速率限制, {current_delay} 秒后重试 "
                            f"({attempt + 1}/{max_attempts})"
                        )
                    else:
                        logger.warning(
                            f"尝试 {attempt + 1}/{max_attempts} 失败: {e}, "
                            f"{current_delay:.1f}秒后重试..."
                        )

                    time.sleep(current_delay)
                    current_delay *= backoff

            # 理论上不会到达这里
            raise RuntimeError("不应该到达这里")

        return wrapper

    return decorator
