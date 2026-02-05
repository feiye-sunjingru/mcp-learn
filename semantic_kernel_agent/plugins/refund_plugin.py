# plugins/refund_plugin.py
from typing import Annotated
from semantic_kernel.functions import kernel_function

class RefundPlugin:
    """退款业务插件（模拟实现）"""

    @kernel_function(description="根据订单ID查询当前退款状态。")
    def get_refund_status(
        self,
        order_id: Annotated[str, "用户的订单唯一标识符，如 'ORD-12345'"]
    ) -> Annotated[str, "返回退款状态，例如 'Processing', 'Completed', 'Rejected'"]:
        # 实际项目中：调用内部退款系统 API 或查询数据库
        if "123" in order_id:
            return "Completed"
        elif "456" in order_id:
            return "Processing"
        else:
            return "No refund request found"

    @kernel_function(description="检查用户是否符合退款资格。")
    def check_refund_eligibility(
        self,
        purchase_date: Annotated[str, "购买日期，格式 YYYY-MM-DD"],
        product_type: Annotated[str, "商品类型，如 'Digital', 'Physical'"]
    ) -> Annotated[str, "返回是否符合资格及原因"]:
        # 简单规则：数字商品 14 天内可退，实体商品 30 天内
        from datetime import datetime, timedelta
        try:
            buy_date = datetime.strptime(purchase_date, "%Y-%m-%d")
            days_since = (datetime.now() - buy_date).days
            if product_type.lower() == "digital" and days_since <= 14:
                return "Eligible for refund."
            elif product_type.lower() == "physical" and days_since <= 30:
                return "Eligible for refund."
            else:
                return f"Not eligible. Purchase was {days_since} days ago."
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD."

    @kernel_function(description="获取公司最新的退款政策摘要。")
    def get_refund_policy_summary(self) -> Annotated[str, "返回退款政策关键条款"]:
        return (
            "• 数字商品：购买后14天内可全额退款\n"
            "• 实体商品：未拆封且30天内可退\n"
            "• 服务类：按使用比例扣除后退款\n"
            "• 退款将在5个工作日内处理"
        )