# 基于 Microsoft Semantic Kernel（SK）的 AI 代理（AI Agent）示例
# 它通过 Azure OpenAI/自定义 OpenAI 兼容 API（如 Gemini 代理服务） 接口调用大语言模型（LLM），并生成自然语言响应
import asyncio, os, sys
from semantic_kernel.agents import ChatCompletionAgent
# from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from dotenv import load_dotenv
import logging, traceback
# 创建标准的消息历史
from semantic_kernel.contents import ChatHistory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_utils.completion import getGemini

load_dotenv()
chat_history = ChatHistory()
logging.basicConfig(level=logging.DEBUG)

async def main():
    agent = ChatCompletionAgent(
        service=getGemini(),
        name="SK-Assistant",
        instructions="You are a helpful assistant.",
    )

    # chat_history.add_user_message("Write a haiku about Semantic Kernel.")
    
    # # 使用更底层的方法
    # result = []
    # async for response in agent.invoke(chat_history):
    #     result.append(response)

    # for res in result:
    #     print(res)

    try:
        # 获取用户消息的响应
        response = await agent.get_response(messages="Write a haiku about Semantic Kernel.用中文输出")
        print(response.content)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

async def debug_api_response():
    import httpx

    api_key = os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("GEMINI_BASE_URL")
    
    # 首先直接测试API端点
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gemini-3-pro",
        "messages": [{"role": "user", "content": "Hello"}],
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(debug_api_response())
