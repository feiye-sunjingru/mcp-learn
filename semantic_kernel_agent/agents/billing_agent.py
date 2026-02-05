# agents/billing_agent.py
from semantic_kernel.agents import ChatCompletionAgent
from llm_utils.completion import getDashScope
from plugins.billing_plugin import BillingPlugin
def create_billing_agent():
    """创建账单处理代理"""
    service = getDashScope()

    return ChatCompletionAgent(
        service=service,
        name="BillingAgent",
        instructions=(
            "你是一个账单专家，专门处理以下问题：\n"
            "- 费用明细\n"
            "- 支付方式\n"
            "- 计费周期\n"
            "- 费用差异\n"
            "- 支付失败原因\n"
            "请用专业、简洁的语言回答。"
        ),
        plugins=[BillingPlugin()],  # ← 注册插件
    )