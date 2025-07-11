"""
Weather Tools Module
Contains all weather-related MCP tools

Author: Andrew Wang
"""

from fastmcp import FastMCP
from remote_api.weather import WeatherClient

# Initialize weather client
weather_client = WeatherClient()


def register_weather_tools(mcp: FastMCP):
    """
    Register weather tools to MCP instance
    
    Args:
        mcp: FastMCP instance
    """
    
    # Get current weather
    @mcp.tool
    def get_current_weather(latitude: float, longitude: float) -> str:
        """
        Get current weather
            Args:
                latitude: Latitude
                longitude: Longitude           
            Returns:
                Weather response data | Error message
        """
        try:
            current_weather = weather_client.get_current_weather(latitude, longitude)
            if current_weather:
                return weather_client.format_current_weather(current_weather)
            return "Unable to get weather information"
        except Exception as e:
            return f"Error getting weather information: {str(e)}"

    # Get daily weather forecast
    @mcp.tool
    def get_daily_weather_forecast(latitude: float, longitude: float, forecast_days: int = 7) -> str:
        """
        Get daily weather forecast
            Args:
                latitude: Latitude
                longitude: Longitude
                forecast_days: Number of forecast days (default 7 days)
            Returns:
                Daily weather forecast data | Error message
        """
        try:
            daily_forecast = weather_client.get_daily_forecast(latitude, longitude, forecast_days)
            if daily_forecast:
                return weather_client.format_daily_forecast(daily_forecast)
            return "Unable to get daily weather forecast"
        except Exception as e:
            return f"Error getting daily weather forecast: {str(e)}"

    # Get hourly weather forecast
    @mcp.tool
    def get_hourly_weather_forecast(latitude: float, longitude: float, forecast_days: int = 3) -> str:
        """
        Get hourly weather forecast
            Args:
                latitude: Latitude
                longitude: Longitude
                forecast_days: Number of forecast days (default 3 days)
            Returns:
                Hourly weather forecast data | Error message
        """
        try:
            hourly_forecast = weather_client.get_hourly_forecast(latitude, longitude, forecast_days)
            if hourly_forecast:
                # Use basic information formatting as there's no dedicated hourly formatting method
                return f"Hourly weather forecast ({hourly_forecast.timezone}):\nLocation: {hourly_forecast.latitude}, {hourly_forecast.longitude}\nElevation: {hourly_forecast.elevation}m\nNote: Detailed hourly data is included in the response"
            return "Unable to get hourly weather forecast"
        except Exception as e:
            return f"Error getting hourly weather forecast: {str(e)}"

    print("✅ Weather tools registered")