# main.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from dotenv import load_dotenv
from agents.triage_agent import create_triage_agent

# 加载环境变量
load_dotenv()

async def main():
    print("🤖 欢迎使用智能客服系统！")
    print("💡 输入 'exit' 退出对话。")
    print("📝 示例问题：'我的账单为什么多了？' 或 '如何申请退款？'\n")

    # 创建分流代理（它内部已包含 Billing 和 Refund 代理）
    triage_agent = create_triage_agent()

    # 共享对话线程（可选，用于多轮上下文）
    thread_id = None

    while True:
        user_input = input("👤 用户: ").strip()
        if user_input.lower() == "exit":
            print("\n👋 再见！")
            break

        if not user_input:
            continue

        try:
            # 获取响应
            response = await triage_agent.get_response(
                messages=user_input,
                thread_id=thread_id
            )
            if response and response.content:
                print(f"💬 助手: {response.content}\n")
            else:
                print("⚠️ 未能生成有效回复。\n")
        except Exception as e:
            print(f"❌ 发生错误: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())