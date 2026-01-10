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


# ==================== MCP 相关 Fixtures ====================

@pytest.fixture
def mcp_test_pdf(tmp_path: Path) -> Path:
    """创建 MCP 测试用的 PDF 文件"""
    pdf_path = tmp_path / "mcp_test.pdf"

    # 尝试从 fixtures 目录读取真实的测试 PDF
    fixtures_pdf = Path(__file__).parent / "fixtures" / "test_document.pdf"

    if fixtures_pdf.exists():
        # 复制真实的测试 PDF
        import shutil
        shutil.copy(fixtures_pdf, pdf_path)
    else:
        # 创建一个最小的 PDF 文件
        pdf_path.write_bytes(
            b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<<>>>>endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer<</Size 4/Root 1 0 R>>
startxref
190
%%EOF"""
        )

    return pdf_path


@pytest.fixture
def reset_config_cache():
    """重置配置缓存 fixture"""
    from ocrbyme.config import reset_settings
    reset_settings()
    yield
    reset_settings()


@pytest.fixture
def mcp_server_params():
    """MCP 服务器参数 fixture"""
    from mcp import StdioServerParameters

    return StdioServerParameters(
        command="python",
        args=["-m", "ocrbyme.mcp_server"],
        env={
            "PYTHONPATH": str(Path(__file__).parent.parent / "src"),
            "DASHSCOPE_API_KEY": os.getenv("DASHSCOPE_API_KEY", "sk-test-key"),
        }
    )


@pytest.fixture
def mock_pdf_processor():
    """Mock PDFProcessor fixture"""
    from unittest.mock import MagicMock
    from ocrbyme.core import PDFProcessor

    mock = MagicMock(spec=PDFProcessor)
    return mock


@pytest.fixture
def mock_ocr_client():
    """Mock QwenVLClient fixture"""
    from unittest.mock import MagicMock
    from ocrbyme.core import QwenVLClient

    mock = MagicMock(spec=QwenVLClient)
    return mock


@pytest.fixture
def mock_markdown_generator():
    """Mock MarkdownGenerator fixture"""
    from unittest.mock import MagicMock
    from ocrbyme.core import MarkdownGenerator

    mock = MagicMock(spec=MarkdownGenerator)
    return mock


@pytest.fixture
def sample_ocr_results():
    """示例 OCR 结果 fixture"""
    return [
        "# Page 1\n\nThis is the content of page 1.",
        "# Page 2\n\nThis is the content of page 2.",
        "# Page 3\n\nThis is the content of page 3.",
    ]


@pytest.fixture
def sample_markdown_output():
    """示例 Markdown 输出 fixture"""
    return """# Document Title

> 由 OCRByMe 生成
> 来源: test.pdf
> 页数: 3
> 生成时间: 2025-01-10 20:30:00

---

## 第 1 页
# Page 1

This is the content of page 1.

---

## 第 2 页
# Page 2

This is the content of page 2.

---

## 第 3 页
# Page 3

This is the content of page 3.

---

<!-- 文档结束 -->
"""


# ==================== pytest 配置 ====================

def pytest_configure(config):
    """pytest 配置钩子"""
    config.addinivalue_line(
        "markers",
        "mcp: 标记为 MCP 服务器相关测试"
    )
    config.addinivalue_line(
        "markers",
        "integration: 标记为集成测试（可能需要真实环境）"
    )
    config.addinivalue_line(
        "markers",
        "slow: 标记为慢速测试"
    )
