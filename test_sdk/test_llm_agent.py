# 基于 Microsoft Semantic Kernel（SK）的 AI 代理（AI Agent）示例
# 它通过 Azure OpenAI/自定义 OpenAI 兼容 API（如 Gemini 代理服务） 接口调用大语言模型（LLM），并生成自然语言响应
import asyncio
import os
from semantic_kernel.agents import ChatCompletionAgent
# from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from openai import AsyncOpenAI

from dotenv import load_dotenv
load_dotenv()


async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("GEMINI_BASE_URL")

    if not api_key:
        print("错误：请设置 GEMINI_API_KEY 环境变量")
    if not base_url:
        print("错误：请设置 GEMINI_BASE_URL 环境变量")

    # 官方 OpenAI Python SDK 的异步客户端
    custom_client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,  # 自定义端点
    )

    # ⚠️ 注意：AzureChatCompletion() 默认会从环境变量读取这些值:AZURE_OPENAI_API_KEY、AZURE_OPENAI_ENDPOINT、AZURE_OPENAI_DEPLOYMENT_NAME
    # 也可以是OpenAIChatCompletion、OllamaChatCompletion、VertexAIChatCompletion等其他聊天补全服务
    service = OpenAIChatCompletion(
        ai_model_id="gemini-3-pro",
        async_client=custom_client
    )
    agent = ChatCompletionAgent(
        service=service,
        name="SK-Assistant",
        instructions="You are a helpful assistant.",
    )

    # 获取用户消息的响应
    response = await agent.get_response(messages="Write a haiku about Semantic Kernel.用中文输出")
    print(response.content)

if __name__ == "__main__":
    asyncio.run(main())
