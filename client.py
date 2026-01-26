import asyncio
import sys
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

# MCP SDK
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LLM 支持
from anthropic import Anthropic

# 环境变量加载
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件中的 API Key


# 创建基本的客户端类
class MCPClient:
    def __init__(self):
        """初始化会话和客户端对象"""
        self.session: Optional[ClientSession] = None
        self.exit_stack: AsyncExitStack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.stdio = None
        self.write = None

    async def connect_to_server(self, server_script_path: str):
        """
        连接 MCP 服务器（支持 Python 或 Node.js 脚本）
        server_script_path: 服务器脚本的路径
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")

        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None,
        )

        # 采用标准输入/输出方式并创建会话
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport

        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        # 列出服务器提供的工具
        response = await self.session.list_tools()
        tools = response.tools
        print(f"\n✅ 已连接服务器，可用工具：{[tool.name for tool in tools]}")

    async def process_query(self, query: str) -> str:
        """
        使用 Claude 和 MCP 工具处理用户查询
        处理查询和工具调用的主要逻辑
        """
        # 1.先把用户问题放入对话上下文
        messages = [
            {
                "role": "user",
                "content": query,
            }
        ]

        # 2.从服务器获取可用工具
        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,  # 注意：元景可能叫 parameters 而非 input_schema
            }
            for tool in response.tools
        ]

        # 3.第一次调用 Claude
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
        )

        # 用于记录过程
        tool_results: List[Dict] = []
        final_text: List[str] = []

        # 4.解析 Claude/元景模型 输出
        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.args or {}

                # 4-1. 调用服务器工具
                try:
                    result = await self.session.call_tool(tool_name, tool_args)
                    tool_results.append({"call": tool_name, "result": result})
                    final_text.append(f"[调用工具 {tool_name}，参数 {tool_args}]")
                except Exception as e:
                    final_text.append(f"[工具调用失败: {e}]")

                # 4-2. 把工具调用的结果发回给 Claude
                if hasattr(content, "text") and content.text:
                    messages.append(
                        {"role": "assistant", "content": content.text}
                    )
                    messages.append(
                        {"role": "user", "content": result.content}
                    )

                # 4-3. Claude 再次回复
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )
                final_text.append(response.content[0].text)

        # 5. 返回最终回答
        return "\n".join(final_text)

    async def chat_loop(self) -> None:
        """
        运行交互式聊天循环
        """
        print("\n🚀 MCP 客户端已启动！")
        print("请输入您的问题，或输入 'quit' 退出。\n")

        while True:
            try:
                query = input("\n❓ 问题: ").strip()
                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print(f"\n💡 回答:\n{response}")

            except Exception as e:
                print(f"\n❌ 错误: {e}")

    async def cleanup(self) -> None:
        """清理资源"""
        await self.exit_stack.aclose()


async def main():
    """主函数：主执行逻辑"""
    if len(sys.argv) < 2:
        print("用法: python client.py <服务器脚本路径>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys
    asyncio.run(main())