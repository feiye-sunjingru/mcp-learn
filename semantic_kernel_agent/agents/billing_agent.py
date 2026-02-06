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
            "你是一个专业的账单专家，必须严格遵循以下规则：\n"
            "1. 所有关于账单金额、费用产生原因的问题，必须使用工具函数回答。\n"
            "2. 当用户询问账单金额时，优先调用 get_latest_bill_amount(user_id) 获取用户最近一笔账单金额，参数：用户ID。\n"
            "3. 当用户询问费用的产生原因时，必须调用 explain_charge(charge_name) 查询，参数：费用名称。\n"
            "4. 不要凭空猜测，必须通过工具获取数据。\n"
            "5. 询问账单详情时，先获取用户账单金额，然后查询每项费用的产生原因，最后给出账单详情。"),
        plugins=[BillingPlugin()],  # ← 注册插件
    )