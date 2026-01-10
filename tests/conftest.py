"""pytest 配置和 fixtures"""

import os
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """临时目录 fixture"""
    yield tmp_path


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """示例 PDF fixture"""
    # 这里可以创建一个测试用的 PDF 文件
    # 实际使用中,可以放置一个真实的测试 PDF
    pdf_path = tmp_path / "sample.pdf"
    # 创建一个空文件作为占位符
    pdf_path.write_bytes(b"")
    return pdf_path


@pytest.fixture
def mock_api_key(monkeypatch: pytest.MonkeyPatch) -> str:
    """Mock API Key fixture"""
    test_key = "sk-test-key-1234567890"
    monkeypatch.setenv("DASHSCOPE_API_KEY", test_key)
    return test_key


@pytest.fixture
def test_image_path(tmp_path: Path) -> Path:
    """测试图片路径 fixture"""
    from PIL import Image

    # 创建一个简单的测试图片
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="white")
    img.save(img_path)
    return img_path
