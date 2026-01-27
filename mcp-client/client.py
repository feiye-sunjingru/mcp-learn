import os
import asyncio
import json
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

# 环境变量加载
from dotenv import load_dotenv
load_dotenv()

# DashScope SDK
import dashscope
from dashscope import Generation

# MCP 协议
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """
    初始化 MCP 客户端类
    """

    def __init__(self):
        self.session: Optional[ClientSession] = None
        # 统一管理异步资源
        self.exit_stack: AsyncExitStack = AsyncExitStack()
        
        # 初始化 DashScope API Key
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 中设置 DASHSCOPE_API_KEY")
        dashscope.api_key = api_key

    """连接到 MCP 服务器并初始化会话"""
    async def connect_to_server(self, server_script_path: str):
        """连接本地 MCP 工具服务器（保持不变）"""
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")

        # 程序支持Python脚本和Node.js脚本作为服务端。它会先检查脚本类型，然后选择相应的启动命令
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[os.path.abspath(server_script_path)],
            env=None,
        )

        # 建立标准输入/输出通信通道
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport

        # 初始化MCP会话
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()

        # 列出服务器提供的全部工具
        response = await self.session.list_tools()
        tools = response.tools
        print(f"\n✅ 已连接 MCP 服务器，可用工具：{[tool.name for tool in tools]}")

    def _call_qwen_sync(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] = None,
        model: str = "qwen-max"
    ) -> Dict[str, Any]:
        """
        同步调用 DashScope Qwen 模型（支持 Tool Calling）
        """
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "result_format": "message",  # 必须！才能返回结构化消息
                "max_tokens": 1000,
                "temperature": 0.7,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = Generation.call(**kwargs)
            
            if response.status_code != 200:
                raise RuntimeError(f"DashScope API 错误: {response.code} - {response.message}")
            
            return response.output.choices[0].message
            
        except Exception as e:
            raise RuntimeError(f"调用 Qwen 失败: {e}")

    async def process_query(self, query: str) -> str:
        """
        使用 Qwen 处理用户查询（原生支持 Tool Calling）
        """
        # 1. 获取可用工具并转换为 OpenAI 格式
        tool_response = await self.session.list_tools()
        tools = []
        for tool in tool_response.tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema  # JSON Schema
                }
            })

        # 2. 构造初始消息
        messages = [{"role": "user", "content": query}]

        # 3. 第一次调用 Qwen（可能触发 tool_calls）
        loop = asyncio.get_event_loop()

        try:
            message = await loop.run_in_executor(None, self._call_qwen_sync, messages, tools)
        except Exception as e:
            return f"❌ LLM 调用失败: {e}"

        # 4. 如果有工具调用，执行工具并回传结果
        if message.get("tool_calls"):
            # 添加 assistant 消息到对话历史
            messages.append(message)

            for tool_call in message["tool_calls"]:
                func = tool_call["function"]
                tool_name = func["name"]
                try:
                    # 注意：arguments 是 JSON 字符串
                    tool_args = json.loads(func["arguments"])
                except json.JSONDecodeError:
                    return f"❌ 工具参数解析失败: {func['arguments']}"

                try:
                    # 调用 MCP 工具
                    tool_result = await self.session.call_tool(tool_name, tool_args)
                    # === 关键修复：提取文本 ===
                    tool_output = ""
                    for item in tool_result.content:
                        if getattr(item, 'type', None) == "text":
                            tool_output += getattr(item, 'text', "")
                        elif isinstance(item, dict) and item.get("type") == "text":
                            tool_output += item.get("text", "")
                    tool_output = tool_output.strip()
                    # =========================
                    
                    # 构造 tool 消息（Qwen 要求 role="tool"）
                    tool_message = {
                        "role": "tool",
                        "content": tool_output,
                        "tool_call_id": tool_call["id"]
                    }
                    messages.append(tool_message)

                except Exception as e:
                    error_msg = f"工具 {tool_name} 调用异常: {e}"
                    messages.append({
                        "role": "tool",
                        "content": error_msg,
                        "tool_call_id": tool_call["id"]
                    })

            # 5. 第二次调用 Qwen 生成最终回答
            try:
                final_message = await loop.run_in_executor(None, self._call_qwen_sync, messages, [])
                return final_message.get("content", "").strip()
            except Exception as e:
                return f"❌ 生成最终回答失败: {e}"

        else:
            # 无工具调用，直接返回
            return message.get("content", "").strip()

    async def chat_loop(self) -> None:
        """交互式聊天循环"""
        print("\n🚀 MCP 客户端（通义千问 Qwen 版）已启动！")
        print("请输入问题，或输入 'quit' 退出。\n")
        while True:
            try:
                query = input("\n❓ 问题: ").strip()
                if query.lower() == "quit":
                    break
                if not query:
                    continue
                response = await self.process_query(query)
                print(f"\n💡 回答:\n{response}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ 运行时错误: {e}")

    async def cleanup(self) -> None:
        """清理资源"""
        await self.exit_stack.aclose()


# ===== 主程序入口 =====
async def main():
    import sys
    # if len(sys.argv) < 2:
    #     print("用法: python qwen_mcp_client.py <mcp_server_script>")
    #     print("示例: python qwen_mcp_client.py ./tools/weather_tool.py")
    #     sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])  #"weather_tool.py"
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())