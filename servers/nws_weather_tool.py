from typing import Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# 创建 FastMCP 服务器实例
mcp = FastMCP("weather")

# 常量定义
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> Optional[dict[str, Any]]:
    """
    向国家气象局 (NWS) 接口发送请求，并做好错误处理。
    
    Args:
        url: 请求地址
        
    Returns:
        JSON 响应字典，失败时返回 None
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP 状态码错误: {e}")
        except Exception as e:
            print(f"发生其他错误: {e}")
    return None


def format_alert(feature: dict) -> str:
    """
    将单条预警信息格式化为易读文本。
    
    Args:
        feature: NWS 预警数据中的 feature 字段
        
    Returns:
        格式化后的字符串
    """
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    获取指定州的恶劣天气警报。
    
    参数:
        state: 两位美国州代码（如 CA、NY）
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "无法获取警报信息或未找到任何警报信息。"

    if not data["features"]:
        return "该州目前没有有效的警报信息。"

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    根据经纬度获取天气预报。
    
    参数:
        latitude: 纬度
        longitude: 经度
    """
    # 获取预报网格端点
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "无法获取此位置的预报信息。"

    # 从points接口响应中获取预报url
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "无法获取详细预报信息。"

    # 将各时段格式转化为可读的预报
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # 仅显示接下来的 5 个时段
        forecast = f"""{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    # 通过标准输入/输出方式启动服务端
    mcp.run(transport="stdio")