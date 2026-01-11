"""增强配置测试"""

import pytest
from ocrbyme.config import get_settings, reset_settings
from ocrbyme.models.types import ConfigurationError


def test_ocr_mode_config(monkeypatch: pytest.MonkeyPatch):
    """测试 OCR 模式配置"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key")
    monkeypatch.setenv("OCRBYME_OCR_MODE", "academic")

    reset_settings()
    settings = get_settings()
    assert settings.ocr_mode == "academic"


def test_default_prompt_property(monkeypatch: pytest.MonkeyPatch):
    """测试 default_prompt 属性兼容性"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key")
    monkeypatch.setenv("OCRBYME_OCR_MODE", "document")

    reset_settings()
    settings = get_settings()
    assert settings.default_prompt == "document"


def test_temperature_config(monkeypatch: pytest.MonkeyPatch):
    """测试温度参数配置"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key")
    monkeypatch.setenv("OCRBYME_TEMPERATURE", "0.0")

    reset_settings()
    settings = get_settings()
    assert settings.temperature == 0.0


def test_image_enhancement_config(monkeypatch: pytest.MonkeyPatch):
    """测试图像增强配置"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key")
    monkeypatch.setenv("OCRBYME_ENABLE_IMAGE_ENHANCEMENT", "true")
    monkeypatch.setenv("OCRBYME_CONTRAST_FACTOR", "1.5")

    reset_settings()
    settings = get_settings()
    assert settings.enable_image_enhancement is True
    assert settings.contrast_factor == 1.5


def test_invalid_temperature(monkeypatch: pytest.MonkeyPatch):
    """测试无效温度参数"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key")
    monkeypatch.setenv("OCRBYME_TEMPERATURE", "3.0")  # 超出范围

    reset_settings()
    with pytest.raises(ConfigurationError) as exc_info:
        get_settings()

    assert "温度" in str(exc_info.value)


def test_invalid_dpi(monkeypatch: pytest.MonkeyPatch):
    """测试无效 DPI 参数"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key")
    monkeypatch.setenv("OCRBYME_DEFAULT_DPI", "700")  # 超出范围

    reset_settings()
    with pytest.raises(ConfigurationError) as exc_info:
        get_settings()

    assert "DPI" in str(exc_info.value)


def test_default_dpi_is_300(monkeypatch: pytest.MonkeyPatch):
    """测试默认 DPI 为 300"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key")

    reset_settings()
    settings = get_settings()
    assert settings.default_dpi == 300


def test_default_ocr_mode_is_academic(monkeypatch: pytest.MonkeyPatch):
    """测试默认 OCR 模式为 academic"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key")

    reset_settings()
    settings = get_settings()
    assert settings.ocr_mode == "academic"


def test_default_image_enhancement_enabled(monkeypatch: pytest.MonkeyPatch):
    """测试默认启用图像增强"""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key")

    reset_settings()
    settings = get_settings()
    assert settings.enable_image_enhancement is True
