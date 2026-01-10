"""重试机制测试"""

import time

import pytest

from ocrbyme.models.types import APIError
from ocrbyme.utils.retry import retry_on_error


def test_retry_on_success() -> None:
    """测试成功时不需要重试"""
    call_count = 0

    @retry_on_error(max_attempts=3, delay=0.01)
    def succeed_on_first_try() -> str:
        nonlocal call_count
        call_count += 1
        return "success"

    result = succeed_on_first_try()

    assert result == "success"
    assert call_count == 1


def test_retry_on_failure() -> None:
    """测试失败后重试"""
    call_count = 0

    @retry_on_error(max_attempts=3, delay=0.01, exceptions=(ValueError,))
    def fail_twice_then_succeed() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Not yet")
        return "success"

    result = fail_twice_then_succeed()

    assert result == "success"
    assert call_count == 3


def test_retry_exhausted() -> None:
    """测试重试次数用尽后抛出异常"""
    call_count = 0

    @retry_on_error(max_attempts=2, delay=0.01, exceptions=(ValueError,))
    def always_fail() -> str:
        nonlocal call_count
        call_count += 1
        raise ValueError("Always fails")

    with pytest.raises(ValueError) as exc_info:
        always_fail()

    assert str(exc_info.value) == "Always fails"
    assert call_count == 2


def test_retry_with_backoff() -> None:
    """测试指数退避"""
    call_count = 0
    call_times = []

    @retry_on_error(max_attempts=3, delay=0.01, backoff=2.0, exceptions=(ValueError,))
    def fail_twice() -> None:
        nonlocal call_count
        call_count += 1
        call_times.append(time.time())
        if call_count < 3:
            raise ValueError("Fail")

    fail_twice()

    # 检查延迟时间是否指数增长
    assert len(call_times) == 3
    # 第一次和第二次之间的延迟
    delay1 = call_times[1] - call_times[0]
    # 第二次和第三次之间的延迟
    delay2 = call_times[2] - call_times[1]

    # delay2 应该大约是 delay1 的 2 倍 (backoff=2.0)
    # 允许一定的误差
    assert delay2 > delay1 * 1.8


def test_no_retry_for_unlisted_exceptions() -> None:
    """测试不在重试列表中的异常不重试"""
    call_count = 0

    @retry_on_error(
        max_attempts=3, delay=0.01, exceptions=(ValueError,)
    )  # 只重试 ValueError
    def raise_key_error() -> None:
        nonlocal call_count
        call_count += 1
        raise KeyError("Not retried")

    with pytest.raises(KeyError):
        raise_key_error()

    # 不应该重试
    assert call_count == 1
