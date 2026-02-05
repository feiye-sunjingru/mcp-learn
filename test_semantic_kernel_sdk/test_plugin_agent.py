# 通过自定义工具（插件）和结构化输出增强我们的代理
import os, sys, asyncio
from typing import Annotated
from pydantic import BaseModel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import OpenAIPromptExecutionSettings  

# 确保项目根目录在模块搜索路径中：Python默认只在该文件所在目录（test_sdk）中查找模块，而 llm_utils 目录位于上级目录，所以需要手动将项目根目录添加到搜索路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_utils.completion import getGoogle, getDashScope

# plugins/menu_plugin.py
from typing import Annotated
from pydantic import BaseModel
from semantic_kernel.functions import kernel_function

class MenuItem(BaseModel):
    """菜单项数据结构"""
    name: str
    price: float

class MenuPlugin:
    """餐厅菜单插件"""

    @kernel_function(
        description="提供当前特色菜品列表（包括汤、沙拉、饮品）。"
    )
    def get_specials(self) -> Annotated[str, "返回特色菜描述文本"]:
        return (
            "Special Soup: Clam Chowder\n"
            "Special Salad: Cobb Salad\n"
            "Special Drink: Chai Tea"
        )

    @kernel_function(
        description="根据菜单项名称查询其价格和名称，返回结构化数据。"
    )
    def get_item_price(
        self,
        menu_item: Annotated[str, "用户询问的菜单项名称，例如 'Clam Chowder' 或 'Cobb Salad'"]
    ) -> MenuItem:
        """
        返回 MenuItem 对象（Pydantic 模型），确保结构化输出。
        实际项目中可连接数据库或 API。
        """
        # 模拟菜单价格表
        menu_db = {
            "clam chowder": MenuItem(name="Clam Chowder", price=8.99),
            "cobb salad": MenuItem(name="Cobb Salad", price=9.99),
            "chai tea": MenuItem(name="Chai Tea", price=4.50),
            "soup": MenuItem(name="Clam Chowder", price=8.99),  # 添加对"soup"的映射
            "special soup": MenuItem(name="Clam Chowder", price=8.99),
        }

        # 标准化输入（转小写）
        key = menu_item.strip().lower()
        
        # 查找匹配项（支持部分匹配）
        for name, item in menu_db.items():
            if key in name or name in key:
                return item

        # 未找到时返回默认
        return MenuItem(name=menu_item, price=0.0)
async def main() -> None:
    # 创建插件化和设置的代理:ChatCompletionAgent 内部自动创建了一个轻量级 Kernel 并管理所有组件！
    agent = ChatCompletionAgent(
        service=getDashScope(),  # 替换为你的聊天补全服务
        name="MenuAssistant",
        instructions=(
            "你是专业餐厅客服助手，必须严格遵循以下规则：\n"
            "1. 所有关于菜单、价格、特色菜的问题，必须使用工具函数回答。\n"
            "2. 当用户询问特色菜或价格时，优先调用 get_specials() 获取特色菜列表。\n"
            "3. 当用户询问具体某道菜的价格时，必须调用 get_item_price() 查询。\n"
            "4. 不要凭空猜测价格，必须通过工具获取数据。\n"
            "5. 询问特色汤品价格时，先获取特色菜列表，然后查询具体价格。"
        ),
        plugins=[MenuPlugin()], # ← 插件注册在这里
    )

    # 创建聊天历史记录
    chat_history = ChatHistory()

    print("欢迎使用餐厅助手！输入 'quit' 或 'exit' 退出对话。")
    print("=" * 50)

    while True:
        # 获取用户输入
        user_input = input("\n您: ")
        
        # 检查退出条件
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("感谢使用餐厅助手，再见！")
            break
        
        # 将用户消息添加到聊天历史
        chat_history.add_user_message(user_input)
        
        print("\n助手: ", end="", flush=True)
        
        # 获取助手响应
        full_response = ""
        async for response in agent.invoke(chat_history):
            if response and response.content:
                full_response += str(response.content)
        
        # 打印助手响应
        print(full_response)
        
        # 将助手的响应也添加到聊天历史中
        if full_response:
            chat_history.add_assistant_message(full_response)

if __name__ == "__main__":
    asyncio.run(main())
