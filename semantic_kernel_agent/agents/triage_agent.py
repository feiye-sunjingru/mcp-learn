# agents/triage_agent.py
import semantic_kernel as sk

from semantic_kernel.agents import ChatCompletionAgent
from agents.billing_agent import create_billing_agent
from agents.refund_agent import create_refund_agent
from llm_utils.completion import getDashScope, getGoogle

def create_triage_agent():
    """创建分流代理（Triage Agent）"""
    # 创建子代理
    billing_agent = create_billing_agent()
    refund_agent = create_refund_agent()

    #⚠️ 注意：Semantic Kernel 中，代理可以作为插件被其他代理调用，这是实现多代理协作的关键。
    return ChatCompletionAgent(
        service=getDashScope(),
        name="TriageAgent",
        instructions=(
            "你是客服系统的智能分流器。\n"
            "1. 分析用户问题属于【账单】还是【退款】。\n"
            "2. 自动调用对应的代理（BillingAgent 或 RefundAgent）。\n"
            "3. 将代理返回的信息整合成完整、友好的回答给用户。\n"
            "4. 如果问题不相关，礼貌告知无法处理。"
        ),
        plugins=[billing_agent, refund_agent],  # 注册子代理作为“插件”
    )