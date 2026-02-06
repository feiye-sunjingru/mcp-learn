# agents/refund_agent.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic_kernel.agents import ChatCompletionAgent
from llm_utils.completion import getDashScope
from plugins.refund_plugin import RefundPlugin

def create_refund_agent():
    """创建退款处理代理"""
    service = getDashScope()

    return ChatCompletionAgent(
        service=getDashScope(),
        name="RefundAgent",
        instructions=(
            "1. 所有关于用户要退款、查询退款状态、检查是否符合退款资格、查询退款政策的问题，必须使用工具函数回答。\n"
            "2. 当用户询问退款状态时，必须调用 get_refund_status(order_id) 获取订单退款状态，参数：订单ID。\n"
            "3. 当需要判断用户是否符合退款资格时，必须调用 check_refund_eligibility(purchase_date, product_type) 查询，参数：购买日期、商品类型。\n"
            "4. 当用户询问退款政策时，必须调用 get_refund_policy_summary() 查询。\n"
            "5. 当用户要直接退款时，必须先检查退款状态，只有未处于退款状态才能继续处理， 然后判断用户是否符合退款资格，只有符合条件才能继续执行，否则返回给用户退款政策信息。\n"
            "6. 不要凭空猜测退款流程，必须通过工具获取数据。\n"
        ),
        plugins=[RefundPlugin()],
    )