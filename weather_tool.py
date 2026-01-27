# weather_tool.py
import asyncio
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent

# 创建FastMCP服务器实例
server = FastMCP("Weather Tool Server")

@server.tool()
async def get_weather(location: str) -> list:
    return [TextContent(type="text", text=f"Weather in {location}: sunny")]


if __name__ == "__main__":
    asyncio.run(server.run())  # 自动使用 stdin/stdout