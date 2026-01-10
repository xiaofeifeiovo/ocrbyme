"""配置模块测试"""

import os
import pytest

from ocrbyme.config import get_settings, reset_settings
from ocrbyme.models.types import ConfigurationError


def test_get_settings_with_valid_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """测试获取有效配置"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key-1234567890")

    # 重置缓存
    reset_settings()

    settings = get_settings()
    assert settings.dashscope_api_key == "sk-test-key-1234567890"
    assert settings.api_base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert settings.model_name == "qwen3-vl-flash"
    assert settings.default_dpi == 200


def test_get_settings_with_invalid_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """测试无效 API Key"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "your_api_key_here")

    # 重置缓存
    reset_settings()

    with pytest.raises(ConfigurationError) as exc_info:
        get_settings()

    assert "DASHSCOPE_API_KEY 未设置" in str(exc_info.value)


def test_get_settings_with_env_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """测试使用环境变量前缀"""
    monkeypatch.setenv("OCRBYME_DASHSCOPE_API_KEY", "sk-test-key-prefix")

    # 确保没有 DASHSCOPE_API_KEY
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)

    # 重置缓存
    reset_settings()

    settings = get_settings()
    assert settings.dashscope_api_key == "sk-test-key-prefix"


def test_custom_dpi_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """测试 DPI 验证"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key-1234567890")
    monkeypatch.setenv("OCRBYME_DEFAULT_DPI", "300")

    # 重置缓存
    reset_settings()

    settings = get_settings()
    assert settings.default_dpi == 300
    settings.validate()  # 不应抛出异常


def test_invalid_dpi(monkeypatch: pytest.MonkeyPatch) -> None:
    """测试无效 DPI"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key-1234567890")
    monkeypatch.setenv("OCRBYME_DEFAULT_DPI", "1000")  # 超出范围

    # 重置缓存
    reset_settings()

    settings = get_settings()

    with pytest.raises(ConfigurationError) as exc_info:
        settings.validate()

    assert "DPI" in str(exc_info.value)
