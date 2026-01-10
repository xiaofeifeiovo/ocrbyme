"""
MCP 服务器手动测试脚本
使用前请设置环境变量：set DASHSCOPE_API_KEY=你的密钥
"""

import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """测试 MCP 服务器连接和工具调用"""

    # 检查 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误: 请先设置 DASHSCOPE_API_KEY 环境变量")
        print("   使用命令: set DASHSCOPE_API_KEY=sk-你的密钥")
        return

    print(f"✅ API Key 已设置: {api_key[:10]}...")

    # MCP 服务器参数
    server_params = StdioServerParameters(
        command="ocrbyme-mcp",
        env={"DASHSCOPE_API_KEY": api_key}
    )

    print("\n🚀 正在启动 OCRByMe MCP 服务器...")

    try:
        # 连接到服务器
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化
                await session.initialize()

                print("✅ MCP 服务器连接成功！\n")

                # 列出可用工具
                tools = await session.list_tools()
                print(f"📦 可用工具数量: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description[:60]}...")

                # 测试 pdf_to_markdown 工具是否存在
                pdf_tool = next((t for t in tools.tools if t.name == "pdf_to_markdown"), None)
                if pdf_tool:
                    print(f"\n✅ 找到 pdf_to_markdown 工具！")
                    print(f"   描述: {pdf_tool.description}")
                    print(f"\n💡 提示: 在 Claude Code 中可以直接使用此工具转换 PDF")
                else:
                    print(f"\n❌ 未找到 pdf_to_markdown 工具")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n💡 可能的原因:")
        print("   1. DASHSCOPE_API_KEY 无效")
        print("   2. ocrbyme-mcp 命令不可用")
        print("   3. 依赖未安装: pip install -e '.[mcp]'")


if __name__ == "__main__":
    print("=" * 60)
    print("OCRByMe MCP 服务器测试工具")
    print("=" * 60)
    asyncio.run(test_mcp_server())
