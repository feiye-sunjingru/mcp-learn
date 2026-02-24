from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.openai import OpenAIChatModel
import asyncio, os
import logfire  # 用于日志监控

# 配置 logfire，便于观察运行时日志
logfire.configure()
logfire.instrument_mcp()
logfire.instrument_pydantic_ai()

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv('DASHSCOPE_BASE_URL')
os.environ["OPENAI_API_KEY"] = api_key
if base_url:
    os.environ["OPENAI_BASE_URL"] = base_url


# 创建 MCP 服务器实例: 通过 Deno 运行 jsr:@pydantic/mcp-run-python 工具, 该工具可以调用系统中已安装的任何 Python 包（如 numpy, pandas, requests 等）
# MCPServerStdio：Pydantic AI 提供的类，用于启动一个通过 stdin/stdout 与外部进程通信的 MCP 服务器
# deno run --allow-net --allow-read --allow-write --node-modules-dir=auto jsr:@pydantic/mcp-run-python stdio
server = MCPServerStdio(
    'deno',
    args=[
        'run',
        '--allow-net',           # 允许网络访问
        '--allow-read',          # 允许读文件
        '--allow-write',         # 允许写文件
        '--node-modules-dir=auto',  # 自动管理 node_modules
        'jsr:@pydantic/mcp-run-python',  # 使用 Pydantic 提供的工具
        'stdio',                 # 标准输入输出
    ],
    timeout=60
)

# 创建 Agent，并将 MCP 服务器注入
model = OpenAIChatModel(model_name='qwen-max')
agent = Agent(model=model, toolsets=[server])

async def main():
    # 启动 MCP 服务器，并自动在退出时关闭
    async with agent:
        # 调用大模型，让其使用 run_python_code 计算日期差
        result = await agent.run('2015-01-01到 2026-02-24一共多少天？')
        print(result.output)  

if __name__ == '__main__':
    asyncio.run(main())