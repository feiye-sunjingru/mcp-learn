import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not API_KEY:
    raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")

def call_dashscope(messages, model="qwen-max"):
    """
    调用通义千问大模型 API
    
    Args:
        messages: 对话历史，格式 [{"role": "user", "content": "..."}]
        model: 模型名称（可选）
    
    Returns:
        str: 模型回复文本
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",          # 注意：不是 Authorization!
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # 解析响应（OpenAI 格式）
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return f"❌ API 返回格式异常: {data}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求失败: {e}"
    except json.JSONDecodeError:
        return f"❌ 非 JSON 响应: {response.text}"
    except KeyError as e:
        return f"❌ 响应字段缺失: {e}, 原始响应: {response.text}"

# 测试用例
if __name__ == "__main__":
    print("🚀 正在测试通义千问大模型 API...\n")
    
    # 测试 1: 简单问答
    print("【测试 1】简单问答")
    messages1 = [{"role": "user", "content": "你好，请介绍一下你自己。"}]
    result1 = call_dashscope(messages1)
    print(f"🤖 回答:\n{result1}\n")
    
    # 测试 2: 数学计算
    print("【测试 2】数学能力")
    messages2 = [{"role": "user", "content": "123 * 456 等于多少？"}]
    result2 = call_dashscope(messages2)
    print(f"🤖 回答:\n{result2}\n")
    
    # 测试 3: 中文创作
    print("【测试 3】中文写作")
    messages3 = [{"role": "user", "content": "写一首关于春天的五言绝句。"}]
    result3 = call_dashscope(messages3)
    print(f"🤖 回答:\n{result3}\n")
    
    print("✅ 测试完成！")