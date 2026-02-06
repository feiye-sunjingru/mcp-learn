# main.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from dotenv import load_dotenv
from agents.triage_agent import create_triage_agent
from semantic_kernel.contents import ChatHistory

# 加载环境变量
load_dotenv()

async def main():
    print("🤖 欢迎使用智能客服系统！")
    print("💡 输入 'exit' 退出对话。")
    print("📝 示例问题：'我的账单为什么多了？' 或 '如何申请退款？'\n")

    # 创建分流代理（它内部已包含 Billing 和 Refund 代理）
    triage_agent = create_triage_agent()
    
    chat_history = ChatHistory()

    while True:
        user_input = input("👤 用户: ").strip()
        if user_input.lower() == "exit":
            print("\n👋 再见！")
            break

        chat_history.add_user_message(user_input)

        # 获取响应
        full_response = ""
        async for response in triage_agent.invoke(chat_history):
            if response and response.content:
                full_response += str(response.content)
        
        if full_response:
            print("🤖 客服:", full_response)
            chat_history.add_assistant_message(full_response)    
        else:
            print("⚠️ 未能生成有效回复。\n")

if __name__ == "__main__":
    asyncio.run(main())