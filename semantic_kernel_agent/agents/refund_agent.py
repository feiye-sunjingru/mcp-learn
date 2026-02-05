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
            "你是一个退款专家，专门处理以下问题：\n"
            "- 退款资格\n"
            "- 退款政策\n"
            "- 退款处理流程\n"
            "- 退款状态查询\n"
            "请提供清晰、合规的指导。"
        ),
        plugins=[RefundPlugin()],
    )