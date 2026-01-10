"""MCP 服务器集成测试 - 需要真实环境"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ocrbyme.config import reset_settings


# ==================== MCP 服务器集成测试 ====================

class TestMCPServerRealIntegration:
    """
    MCP 服务器真实集成测试

    这些测试需要：
    1. 有效的 DASHSCOPE_API_KEY 环境变量
    2. 完整的项目依赖安装
    3. 可访问的 PDF 文件（用于真实测试）

    运行方式：
        pytest tests/test_mcp_integration.py -v -s
    """

    @pytest.fixture
    def server_params(self):
        """获取 MCP 服务器参数"""
        # 使用 Python 模块方式运行，确保在虚拟环境中
        return StdioServerParameters(
            command="python",
            args=["-m", "ocrbyme.mcp_server"],
            env={
                "PYTHONPATH": str(Path(__file__).parent.parent / "src"),
                "DASHSCOPE_API_KEY": os.getenv("DASHSCOPE_API_KEY", ""),
            }
        )

    @pytest.fixture
    def test_pdf_path(self):
        """获取测试 PDF 文件路径"""
        # 创建一个简单的测试 PDF
        # 在实际测试中，你应该使用真实的 PDF 文件
        pdf_path = Path(__file__).parent / "fixtures" / "test_document.pdf"

        if not pdf_path.exists():
            pytest.skip(f"测试 PDF 文件不存在: {pdf_path}")

        return pdf_path

    @pytest.mark.skipif(
        os.getenv("DASHSCOPE_API_KEY") is None,
        reason="需要 DASHSCOPE_API_KEY 环境变量"
    )
    @pytest.mark.asyncio
    async def test_server_initialization(self, server_params):
        """测试服务器可以正常初始化"""
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化会话
                await session.initialize()

                # 验证服务器已连接
                assert session is not None

    @pytest.mark.skipif(
        os.getenv("DASHSCOPE_API_KEY") is None,
        reason="需要 DASHSCOPE_API_KEY 环境变量"
    )
    @pytest.mark.asyncio
    async def test_list_tools(self, server_params):
        """测试列出可用工具"""
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 列出工具
                response = await session.list_tools()

                # 验证工具列表
                assert response.tools is not None
                assert len(response.tools) > 0

                # 检查是否有 pdf_to_markdown 工具
                tool_names = [tool.name for tool in response.tools]
                assert "pdf_to_markdown" in tool_names

                # 验证工具元数据
                pdf_tool = next(t for t in response.tools if t.name == "pdf_to_markdown")
                assert pdf_tool.description is not None
                assert len(pdf_tool.inputSchema) > 0

    @pytest.mark.skipif(
        os.getenv("DASHSCOPE_API_KEY") is None,
        reason="需要 DASHSCOPE_API_KEY 环境变量"
    )
    @pytest.mark.asyncio
    async def test_pdf_to_markdown_tool_call(self, server_params, test_pdf_path):
        """测试调用 pdf_to_markdown 工具"""
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 调用工具
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_path = Path(temp_dir) / "output.md"

                    result = await session.call_tool(
                        "pdf_to_markdown",
                        {
                            "pdf_path": str(test_pdf_path),
                            "output_path": str(output_path),
                            "dpi": 200,
                            "extract_images": False,
                            "timeout": 60
                        }
                    )

                    # 验证返回结果
                    assert result.content is not None
                    assert len(result.content) > 0

                    # 解析 JSON 结果
                    import json
                    result_data = json.loads(result.content[0].text)

                    # 验证结果结构
                    assert "success" in result_data
                    assert "output_path" in result_data

                    # 如果成功，检查输出文件是否存在
                    if result_data["success"]:
                        assert Path(result_data["output_path"]).exists()
                    else:
                        # 失败时应该有错误信息
                        assert "error" in result_data

    @pytest.mark.skipif(
        os.getenv("DASHSCOPE_API_KEY") is None,
        reason="需要 DASHSCOPE_API_KEY 环境变量"
    )
    @pytest.mark.asyncio
    async def test_pdf_to_markdown_with_page_range(self, server_params, test_pdf_path):
        """测试指定页码范围的转换"""
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                with tempfile.TemporaryDirectory() as temp_dir:
                    output_path = Path(temp_dir) / "output_pages.md"

                    # 只转换第 1 页
                    result = await session.call_tool(
                        "pdf_to_markdown",
                        {
                            "pdf_path": str(test_pdf_path),
                            "output_path": str(output_path),
                            "pages": "1",
                            "dpi": 200
                        }
                    )

                    import json
                    result_data = json.loads(result.content[0].text)

                    if result_data["success"]:
                        # 验证只处理了 1 页
                        assert result_data["page_count"] == 1

    @pytest.mark.skipif(
        os.getenv("DASHSCOPE_API_KEY") is None,
        reason="需要 DASHSCOPE_API_KEY 环境变量"
    )
    @pytest.mark.asyncio
    async def test_pdf_to_markdown_error_handling(self, server_params):
        """测试错误处理"""
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 测试不存在的文件
                result = await session.call_tool(
                    "pdf_to_markdown",
                    {
                        "pdf_path": "C:\\nonexistent\\file.pdf"
                    }
                )

                import json
                result_data = json.loads(result.content[0].text)

                # 应该返回错误
                assert result_data["success"] is False
                assert "error" in result_data
                assert "不存在" in result_data["error"]


# ==================== 性能测试 ====================

class TestMCPServerPerformance:
    """MCP 服务器性能测试"""

    @pytest.fixture
    def server_params(self):
        return StdioServerParameters(
            command="python",
            args=["-m", "ocrbyme.mcp_server"],
            env={
                "PYTHONPATH": str(Path(__file__).parent.parent / "src"),
                "DASHSCOPE_API_KEY": os.getenv("DASHSCOPE_API_KEY", ""),
            }
        )

    @pytest.mark.skipif(
        os.getenv("DASHSCOPE_API_KEY") is None,
        reason="需要 DASHSCOPE_API_KEY 环境变量"
    )
    @pytest.mark.asyncio
    async def test_server_startup_time(self, server_params):
        """测试服务器启动时间"""
        import time

        start_time = time.time()

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

        startup_time = time.time() - start_time

        # 服务器启动应该在合理时间内完成（例如 5 秒）
        assert startup_time < 5.0, f"服务器启动时间过长: {startup_time:.2f}s"

    @pytest.mark.skipif(
        os.getenv("DASHSCOPE_API_KEY") is None,
        reason="需要 DASHSCOPE_API_KEY 环境变量"
    )
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, server_params):
        """测试并发请求处理"""
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 并发列出工具
                tasks = [
                    session.list_tools()
                    for _ in range(5)
                ]

                results = await asyncio.gather(*tasks)

                # 所有请求都应该成功
                assert len(results) == 5
                for result in results:
                    assert result.tools is not None


# ==================== 配置测试 ====================

class TestMCPConfiguration:
    """测试 MCP 配置"""

    def test_environment_variable_required(self):
        """测试环境变量是必需的"""
        # 临时删除环境变量
        original_key = os.getenv("DASHSCOPE_API_KEY")
        original_ocrbyme_key = os.getenv("OCRBYME_DASHSCOPE_API_KEY")

        try:
            if "DASHSCOPE_API_KEY" in os.environ:
                del os.environ["DASHSCOPE_API_KEY"]
            if "OCRBYME_DASHSCOPE_API_KEY" in os.environ:
                del os.environ["OCRBYME_DASHSCOPE_API_KEY"]

            reset_settings()

            from ocrbyme.mcp_server import get_mcp_settings
            from ocrbyme.models.types import ConfigurationError

            with pytest.raises(ConfigurationError):
                get_mcp_settings()

        finally:
            # 恢复环境变量
            if original_key is not None:
                os.environ["DASHSCOPE_API_KEY"] = original_key
            if original_ocrbyme_key is not None:
                os.environ["OCRBYME_DASHSCOPE_API_KEY"] = original_ocrbyme_key

            reset_settings()


# ==================== 手动测试辅助函数 ====================

class TestManualTestingHelpers:
    """手动测试辅助函数"""

    @staticmethod
    async def test_with_real_pdf(pdf_path: str, output_path: str = None):
        """
        手动测试：使用真实 PDF 文件测试

        用法：
            python -c "
            import asyncio
            from tests.test_mcp_integration import TestManualTestingHelpers

            async def test():
                await TestManualTestingHelpers.test_with_real_pdf(
                    pdf_path='C:/path/to/your/document.pdf',
                    output_path='C:/path/to/output.md'
                )

            asyncio.run(test())
            "
        """
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "ocrbyme.mcp_server"],
            env={
                "PYTHONPATH": str(Path(__file__).parent.parent / "src"),
            }
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 列出工具
                tools = await session.list_tools()
                print(f"可用工具: {[t.name for t in tools.tools]}")

                # 调用转换工具
                result = await session.call_tool(
                    "pdf_to_markdown",
                    {
                        "pdf_path": pdf_path,
                        "output_path": output_path,
                        "dpi": 200,
                    }
                )

                import json
                result_data = json.loads(result.content[0].text)
                print(f"转换结果: {json.dumps(result_data, indent=2, ensure_ascii=False)}")

                return result_data

    @staticmethod
    async def test_tool_schema():
        """
        手动测试：查看工具的详细 schema

        用法：
            python -c "
            import asyncio
            from tests.test_mcp_integration import TestManualTestingHelpers

            asyncio.run(TestManualTestingHelpers.test_tool_schema())
            "
        """
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "ocrbyme.mcp_server"],
            env={
                "PYTHONPATH": str(Path(__file__).parent.parent / "src"),
            }
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()

                for tool in tools.tools:
                    print(f"\n工具名称: {tool.name}")
                    print(f"描述: {tool.description}")
                    print(f"输入 Schema:")
                    import json
                    print(json.dumps(tool.inputSchema, indent=2, ensure_ascii=False))


# ==================== 夹具和工具 ====================

@pytest.fixture
def sample_pdf_content():
    """生成示例 PDF 内容（用于测试）"""
    # 这是一个最小的 PDF 文件示例
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000056 00000 n
0000000115 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF"""


@pytest.fixture
def create_temp_pdf(sample_pdf_content, tmp_path):
    """创建临时 PDF 文件"""
    def _create_pdf(filename="test.pdf"):
        pdf_path = tmp_path / filename
        pdf_path.write_bytes(sample_pdf_content)
        return pdf_path

    return _create_pdf


if __name__ == "__main__":
    # 运行手动测试
    print("=== MCP 服务器手动测试 ===\n")

    print("1. 测试工具 Schema")
    print("运行: python -c 'import asyncio; from tests.test_mcp_integration import TestManualTestingHelpers; asyncio.run(TestManualTestingHelpers.test_tool_schema())'")

    print("\n2. 测试真实 PDF 转换")
    print("运行: python -c \"import asyncio; from tests.test_mcp_integration import TestManualTestingHelpers; asyncio.run(TestManualTestingHelpers.test_with_real_pdf('path/to/your.pdf'))\"")

    print("\n3. 运行所有集成测试")
    print("运行: pytest tests/test_mcp_integration.py -v -s")
