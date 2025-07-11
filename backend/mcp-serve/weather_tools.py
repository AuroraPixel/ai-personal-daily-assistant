"""
天气工具模块 (Weather Tools Module)
包含所有天气相关的MCP工具
"""

from fastmcp import FastMCP
from remote_api.weather import WeatherClient

# 初始化天气客户端 (Initialize weather client)
weather_client = WeatherClient()


def register_weather_tools(mcp: FastMCP):
    """
    注册天气工具到MCP实例
    Register weather tools to MCP instance
    
    Args:
        mcp: FastMCP实例
    """
    
    # 获取当前天气 (Get current weather)
    @mcp.tool
    def get_current_weather(latitude: float, longitude: float) -> str:
        """
        获取当前天气
            Args:
                latitude: 纬度
                longitude: 经度           
            Returns:
                天气响应数据 | 错误信息
        """
        try:
            current_weather = weather_client.get_current_weather(latitude, longitude)
            if current_weather:
                return weather_client.format_current_weather(current_weather)
            return "无法获取天气信息"
        except Exception as e:
            return f"获取天气信息时出错: {str(e)}"

    # 获取每日天气预报 (Get daily weather forecast)
    @mcp.tool
    def get_daily_weather_forecast(latitude: float, longitude: float, forecast_days: int = 7) -> str:
        """
        获取每日天气预报
            Args:
                latitude: 纬度
                longitude: 经度
                forecast_days: 预报天数 (默认7天)
            Returns:
                每日天气预报数据 | 错误信息
        """
        try:
            daily_forecast = weather_client.get_daily_forecast(latitude, longitude, forecast_days)
            if daily_forecast:
                return weather_client.format_daily_forecast(daily_forecast)
            return "无法获取每日天气预报"
        except Exception as e:
            return f"获取每日天气预报时出错: {str(e)}"

    # 获取每小时天气预报 (Get hourly weather forecast)
    @mcp.tool
    def get_hourly_weather_forecast(latitude: float, longitude: float, forecast_days: int = 3) -> str:
        """
        获取每小时天气预报
            Args:
                latitude: 纬度
                longitude: 经度
                forecast_days: 预报天数 (默认3天)
            Returns:
                每小时天气预报数据 | 错误信息
        """
        try:
            hourly_forecast = weather_client.get_hourly_forecast(latitude, longitude, forecast_days)
            if hourly_forecast:
                # 使用基本信息格式化，因为没有专门的hourly格式化方法
                return f"每小时天气预报 ({hourly_forecast.timezone}):\n位置: {hourly_forecast.latitude}, {hourly_forecast.longitude}\n海拔: {hourly_forecast.elevation}m\n注意: 详细的每小时数据包含在响应中"
            return "无法获取每小时天气预报"
        except Exception as e:
            return f"获取每小时天气预报时出错: {str(e)}"

    print("✅ 天气工具已注册 (Weather tools registered)")