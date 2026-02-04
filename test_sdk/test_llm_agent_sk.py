# main.py
import asyncio
import os, sys
from semantic_kernel.agents import ChatCompletionAgent
import semantic_kernel as sk
# 创建标准的消息历史
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_utils.completion import getGemini
async def main():
    # Semantic Kernel Python SDK 在 v1.x 中对 Kernel 做了自动封装
    # 使用ChatCompletionAgent 替代了 kernel()+add_service() + agent(kernel=...)
    kernel = sk.Kernel()
    service = getGemini()
    kernel.add_service(service)

    agent = ChatCompletionAgent(
        kernel=kernel,                      # ← 关键：显式传入 kernel
        name="SK-Agent",
        instructions="You are a helpful assistant.",
    )

    # 使用更底层的方法
    full_response = ""
    async for response in agent.invoke("Write a haiku about Semantic Kernel."):
        if response and response.content:
            full_response += str(response.content)
    
    print(full_response)

if __name__ == "__main__":
    asyncio.run(main())