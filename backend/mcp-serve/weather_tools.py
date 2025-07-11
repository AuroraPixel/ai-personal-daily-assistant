"""
Weather Tools Module
Contains all weather-related MCP tools

Author: Andrew Wang
"""

import json
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
        Get current weather conditions
        
        Args:
            latitude: Location latitude in decimal degrees (e.g., 40.7128 for New York)
            longitude: Location longitude in decimal degrees (e.g., -74.0060 for New York)
            
        Returns:
            JSON string of WeatherApiResponse entity in format:
            {
                "latitude": 40.710335,
                "longitude": -73.99309,
                "timezone": "GMT",
                "elevation": 32,
                "current_weather_units": {
                    "time": "iso8601",
                    "temperature": "°C",
                    "windspeed": "km/h",
                    "winddirection": "°",
                    "is_day": "",
                    "weathercode": "wmo code"
                },
                "current_weather": {
                    "time": "2025-07-11T03:30",
                    "temperature": 22.7,
                    "windspeed": 5.6,
                    "winddirection": 130,
                    "is_day": 0,
                    "weathercode": 3
                }
            }
        """
        try:
            result = weather_client.get_current_weather(latitude, longitude)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": "Unable to get current weather information"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting current weather: {str(e)}"}, ensure_ascii=False)

    # Get daily weather forecast
    @mcp.tool
    def get_daily_weather_forecast(latitude: float, longitude: float, forecast_days: int = 7) -> str:
        """
        Get daily weather forecast
        
        Args:
            latitude: Location latitude in decimal degrees (e.g., 40.7128 for New York)
            longitude: Location longitude in decimal degrees (e.g., -74.0060 for New York)
            forecast_days: Number of forecast days (1-16, default 7)
            
        Returns:
            JSON string of WeatherApiResponse entity in format:
            {
                "latitude": 40.710335,
                "longitude": -73.99309,
                "timezone": "GMT",
                "elevation": 32,
                "daily_units": {
                    "time": "iso8601",
                    "temperature_2m_max": "°C",
                    "temperature_2m_min": "°C",
                    "precipitation_sum": "mm",
                    "weathercode": "wmo code"
                },
                "daily": {
                    "time": ["2025-07-11", "2025-07-12", ...],
                    "temperature_2m_max": [29.9, 29.1, ...],
                    "temperature_2m_min": [21.6, 22, ...],
                    "precipitation_sum": [0, 0, ...],
                    "weathercode": [3, 45, ...]
                }
            }
        """
        try:
            result = weather_client.get_daily_forecast(latitude, longitude, forecast_days)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": "Unable to get daily weather forecast"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting daily weather forecast: {str(e)}"}, ensure_ascii=False)

    # Get hourly weather forecast
    @mcp.tool
    def get_hourly_weather_forecast(latitude: float, longitude: float, forecast_days: int = 3) -> str:
        """
        Get hourly weather forecast
        
        Args:
            latitude: Location latitude in decimal degrees (e.g., 40.7128 for New York)
            longitude: Location longitude in decimal degrees (e.g., -74.0060 for New York)
            forecast_days: Number of forecast days (1-16, default 3)
            
        Returns:
            JSON string of WeatherApiResponse entity in format:
            {
                "latitude": 40.710335,
                "longitude": -73.99309,
                "timezone": "GMT",
                "elevation": 32,
                "hourly_units": {
                    "time": "iso8601",
                    "temperature_2m": "°C",
                    "precipitation": "mm",
                    "weathercode": "wmo code",
                    "windspeed_10m": "km/h"
                },
                "hourly": {
                    "time": ["2025-07-11T00:00", "2025-07-11T01:00", ...],
                    "temperature_2m": [22.7, 22.1, ...],
                    "precipitation": [0, 0, ...],
                    "weathercode": [3, 3, ...],
                    "windspeed_10m": [5.6, 6.2, ...]
                }
            }
        """
        try:
            result = weather_client.get_hourly_forecast(latitude, longitude, forecast_days)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": "Unable to get hourly weather forecast"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting hourly weather forecast: {str(e)}"}, ensure_ascii=False)

    print("✅ Weather tools registered")