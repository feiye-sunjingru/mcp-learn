# plugins/billing_plugin.py
from typing import Annotated
from semantic_kernel.functions import kernel_function

class BillingPlugin:
    """账单查询插件（模拟）"""

    @kernel_function(description="根据用户ID查询最近一笔账单金额。")
    def get_latest_bill_amount(
        self,
        user_id: Annotated[str, "用户的唯一标识符"]
    ) -> Annotated[str, "返回账单金额，格式如 '$49.99'"]:
        # 实际项目中：连接数据库或内部 API
        return "$49.99"

    @kernel_function(description="解释某项费用的产生原因。")
    def explain_charge(
        self,
        charge_name: Annotated[str, "费用名称，如 'Premium Subscription'"]
    ) -> Annotated[str, "费用说明"]:
        if "Premium" in charge_name:
            return "这是您升级到高级订阅计划的月度费用。"
        return "这是一项标准服务费用。"