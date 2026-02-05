from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
import os
from dotenv import load_dotenv

load_dotenv()
def getGoogle():
    api_key = os.getenv("GOOGLE_API_KEY")
    base_url = os.getenv("GOOGLE_BASE_URL")

    if not api_key:
        print("错误：请设置 GOOGLE_API_KEY 环境变量")
    if not base_url:
        print("错误：请设置 GOOGLE_BASE_URL 环境变量")

    # 官方 OpenAI Python SDK 的异步客户端
    custom_client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,  # 自定义端点
    )

    # ⚠️ 注意：AzureChatCompletion() 默认会从环境变量读取这些值:AZURE_OPENAI_API_KEY、AZURE_OPENAI_ENDPOINT、AZURE_OPENAI_DEPLOYMENT_NAME
    # 也可以是OpenAIChatCompletion、OllamaChatCompletion等其他聊天补全服务
    service = OpenAIChatCompletion(
        ai_model_id="gemini-3-pro",
        async_client=custom_client,
        service_id="gemini_service"
    )

    return service

def getOpenAI():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not api_key:
        print("错误：请设置 OPENAI_API_KEY 环境变量")
    if not base_url:
        print("错误：请设置 OPENAI_BASE_URL 环境变量")

    custom_client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,  # 自定义端点
    )

    # ⚠️ 注意：AzureChatCompletion() 默认会从环境变量读取这些值:AZURE_OPENAI_API_KEY、AZURE_OPENAI_ENDPOINT、AZURE_OPENAI_DEPLOYMENT_NAME
    # 也可以是OpenAIChatCompletion、OllamaChatCompletion、VertexAIChatCompletion等其他聊天补全服务
    service = OpenAIChatCompletion(
        ai_model_id="gpt-4o-mini",
        async_client=custom_client,
        service_id="openai_service"
    )

def getDashScope():
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_BASE_URL")

    if not api_key:
        print("错误：请设置 DASHSCOPE_API_KEY 环境变量")
    if not base_url:
        print("错误：请设置 DASHSCOPE_BASE_URL 环境变量")
    custom_client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,  # 自定义端点
    )

    service = OpenAIChatCompletion(
        ai_model_id="qwen-turbo",
        async_client=custom_client,
        service_id="dashscope_service"
    )

    return service
