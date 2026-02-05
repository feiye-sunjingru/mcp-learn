# 导入 Semantic Kernel 库并命名为 sk，这是一个用于 AI 编排的框架
import semantic_kernel as sk
import os
import asyncio
from openai import AsyncOpenAI
# 从 Semantic Kernel 中导入 OpenAI 相关组件：聊天补全服务和提示执行设置
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelFunction
from dotenv import load_dotenv
from semantic_kernel.exceptions import KernelInvokeException

# 调用 load_dotenv() 函数加载 .env 文件中的环境变量到程序中
load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not API_KEY:
    raise ValueError("请设置有效的 DASHSCOPE_API_KEY")

# 创建 Semantic Kernel 实例，这是整个 AI 服务的核心管理器
kernel = sk.Kernel()

# 创建 AsyncOpenAI 客户端实例，配置 API 密钥和通义千问兼容模式的 API 地址
client = AsyncOpenAI(
    # 设置 API 密钥为之前获取的 DASHSCOPE_API_KEY
    api_key=API_KEY,
    # 设置基础 URL 为阿里云通义千问的兼容模式接口地址
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 创建 OpenAIChatCompletion 服务实例，连接到通义千问 API
service = OpenAIChatCompletion(
    # 指定要使用的模型 ID（这里是 qwen-turbo 模型）
    ai_model_id="qwen-turbo", 
    # 使用上面创建的 AsyncOpenAI 客户端
    async_client=client,
    # 为该服务设置唯一标识符
    service_id="fy1234567"
)
# 将创建的服务添加到 kernel 中进行管理
kernel.add_service(service)

# 定义一个提示模板字符串，{{ $input }} 是变量占位符，会被实际输入替换
prompt = "将以下英文翻译成中文：{{$input}}"
# 基于提示模板创建一个翻译函数
translate_function = KernelFunction.from_prompt(
    # 设置函数名称
    function_name="translate",
    # 设置插件名称
    plugin_name="TranslationPlugin",
    prompt=prompt
)

async def main():
    try:
        # 调用 kernel.invoke 方法执行 translate_function 函数
        result = await kernel.invoke(
            translate_function,
            # 设置输入参数
            input="Hello, how are you?"
        )
        print("✅ 翻译结果:", str(result))
    except KernelInvokeException as e:
        print("❌ 调用失败")
        print(f"详细信息: {e}")

if __name__ == "__main__":
    # 使用 asyncio.run 运行 main 异步函数
    asyncio.run(main())