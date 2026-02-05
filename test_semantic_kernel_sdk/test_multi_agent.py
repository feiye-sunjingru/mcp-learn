import asyncio
from semantic_kernel.agents import ChatCompletionAgent
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_utils.completion import getDashScope, getGoogle

# 创建账单代理
billing_agent = ChatCompletionAgent(
    service=getDashScope(),  # 使用 DashScope 服务
    name="BillingAgent",
    instructions="处理账单问题，如费用、支付方式、周期、费用差异和支付失败等。"
)

# 创建退款代理
refund_agent = ChatCompletionAgent(
    service=getDashScope(),
    name="RefundAgent",
    instructions="协助用户处理退款查询，包括资格、政策、处理和状态更新等。"
)

# 创建分诊代理，并将其他两个代理作为插件注册
triage_agent = ChatCompletionAgent(
    service=getGoogle(),
    name="TriageAgent",
    instructions=(
        "评估用户请求，并将它们转发给 BillingAgent 或 RefundAgent，"
        "以获得针对性的帮助。\n"
        "将代理提供的任意信息都包含在完整的答案中并提供给用户。"
    ),
    plugins=[billing_agent, refund_agent],
)

async def main() -> None:
    print("欢迎使用聊天机器人！\n 输入'exit'退出。\n 尝试获取一些账单或退款帮助。")

    while True:
        user_input = input("用户>: ")

        if user_input.lower().strip() == "exit":
            print("\n\n正在退出聊天……")
            return False

        response = await triage_agent.get_response(
            messages=user_input,
            thread=None,
        )

        if response:
            print(f"代理 => {response}")

if __name__ == "__main__":
    asyncio.run(main())