from zai import ZhipuAiClient
import os

from dotenv import load_dotenv
load_dotenv()


# 从环境变量读取 API Key
API_KEY = os.getenv("ZAI_API_KEY")
client = ZhipuAiClient(api_key=API_KEY)

def call_zhipu(messages, model="glm-4.7-flash") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=False,
        max_tokens=512,
        temperature=0.7
    )
    return response.choices[0].message.content


# 测试用例
if __name__ == "__main__":
    print("🚀 正在测试智谱大模型 API...\n")
    
    # 测试 1: 简单问答
    print("【测试 1】简单问答")
    messages1 = [{"role": "user", "content": "你好，请介绍一下你自己。"}]
    result1 = call_zhipu(messages1)
    print(f"🤖 回答:\n{result1}\n")
    
    # 测试 2: 数学计算
    print("【测试 2】数学能力")
    messages2 = [{"role": "user", "content": "123 * 456 等于多少？"}]
    result2 = call_zhipu(messages2)
    print(f"🤖 回答:\n{result2}\n")
    
    # 测试 3: 中文创作
    print("【测试 3】中文写作")
    messages3 = [{"role": "user", "content": "写一首关于春天的五言绝句。"}]
    result3 = call_zhipu(messages3)
    print(f"🤖 回答:\n{result3}\n")
    
    print("✅ 测试完成！")

