"""
Weather API Client

Author: Andrew Wang
"""

from typing import Optional, List
from core.http_core.client import APIClient
from .models import WeatherRequest, WeatherResponse, weather_response_from_dict, get_weather_description


class WeatherClient:
    """Open-Meteo Weather API Client"""
    
    def __init__(self):
        self.client = APIClient("https://api.open-meteo.com/v1")
    
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[WeatherResponse]:
        """
        Get current weather
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            Weather response data or None
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True
        }
        
        data = self.client.get("/forecast", params=params)
        if data:
            return weather_response_from_dict(data)
        return None
    
    def get_weather_forecast(self, latitude: float, longitude: float, 
                           forecast_days: int = 7,
                           daily_vars: Optional[List[str]] = None,
                           hourly_vars: Optional[List[str]] = None) -> Optional[WeatherResponse]:
        """
        Get weather forecast
        
        Args:
            latitude: Latitude
            longitude: Longitude
            forecast_days: Number of forecast days
            daily_vars: List of daily variables
            hourly_vars: List of hourly variables
            
        Returns:
            Weather response data or None
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": forecast_days
        }
        
        if daily_vars:
            params["daily"] = ",".join(daily_vars)
        
        if hourly_vars:
            params["hourly"] = ",".join(hourly_vars)
        
        data = self.client.get("/forecast", params=params)
        if data:
            return weather_response_from_dict(data)
        return None
    
    def get_daily_forecast(self, latitude: float, longitude: float, 
                          forecast_days: int = 7) -> Optional[WeatherResponse]:
        """
        Get daily weather forecast
        
        Args:
            latitude: Latitude
            longitude: Longitude
            forecast_days: Number of forecast days
            
        Returns:
            Weather response data or None
        """
        daily_vars = [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "weathercode",
            "sunrise",
            "sunset"
        ]
        
        return self.get_weather_forecast(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            daily_vars=daily_vars
        )
    
    def get_hourly_forecast(self, latitude: float, longitude: float, 
                           forecast_days: int = 3) -> Optional[WeatherResponse]:
        """
        Get hourly weather forecast
        
        Args:
            latitude: Latitude
            longitude: Longitude
            forecast_days: Number of forecast days
            
        Returns:
            Weather response data or None
        """
        hourly_vars = [
            "temperature_2m",
            "precipitation",
            "weathercode",
            "windspeed_10m"
        ]
        
        return self.get_weather_forecast(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            hourly_vars=hourly_vars
        )
    
    def format_current_weather(self, weather_response: WeatherResponse) -> str:
        """
        Format current weather information
        
        Args:
            weather_response: Weather response data
            
        Returns:
            Formatted weather information string
        """
        if not weather_response.current_weather:
            return "Current weather data unavailable"
        
        current = weather_response.current_weather
        description = get_weather_description(current.weathercode)
        day_night = "Day" if current.is_day else "Night"
        
        return f"""
Current Weather ({weather_response.timezone}):
Time: {current.time}
Weather: {description}
Temperature: {current.temperature}°C
Wind Speed: {current.windspeed} km/h
Wind Direction: {current.winddirection}°
Period: {day_night}
Location: {weather_response.latitude}, {weather_response.longitude}
Elevation: {weather_response.elevation}m
        """.strip()
    
    def format_daily_forecast(self, weather_response: WeatherResponse) -> str:
        """
        Format daily weather forecast
        
        Args:
            weather_response: Weather response data
            
        Returns:
            Formatted forecast information string
        """
        if not weather_response.daily:
            return "Daily weather forecast data unavailable"
        
        daily = weather_response.daily
        forecast_lines = [f"Daily Weather Forecast ({weather_response.timezone}):"]
        
        for i, date in enumerate(daily.time):
            line = f"Date: {date}"
            
            if daily.temperature_2m_max and daily.temperature_2m_min:
                line += f", Temperature: {daily.temperature_2m_min[i]}°C - {daily.temperature_2m_max[i]}°C"
            
            if daily.precipitation_sum:
                line += f", Precipitation: {daily.precipitation_sum[i]}mm"
            
            if daily.weathercode:
                description = get_weather_description(daily.weathercode[i])
                line += f", Weather: {description}"
            
            if daily.sunrise and daily.sunset:
                line += f", Sunrise: {daily.sunrise[i]}, Sunset: {daily.sunset[i]}"
            
            forecast_lines.append(line)
        
        return "\n".join(forecast_lines) 