from mcpi.server import Server, Tool, Resource, Prompt
import asyncio
import json

# 定义一个简单工具
async def get_weather(location: str) -> str:
    return f"☀️ {location} 的天气晴朗，25°C"

# 创建 Server 实例
server = Server("my-weather-server")

# 注册工具
@server.tool()
async def weather_tool(arguments: dict) -> dict:
    location = arguments["location"]
    result = await get_weather(location)
    return {"content": result}

# 注册资源（可选）
@server.resource("readme")
async def readme_resource() -> str:
    return "# 我的天气助手\n提供实时天气查询。"

# 注册提示模板（可选）
@server.prompt("weather_summary")
async def weather_prompt(args: dict) -> str:
    return f"请用友好的语气总结天气：{args['weather']}"

# 启动（自动支持 stdin/stdout 和 WebSocket）
if __name__ == "__main__":
    asyncio.run(server.run())