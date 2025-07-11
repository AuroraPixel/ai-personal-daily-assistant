"""
Weather API Client

Author: Andrew Wang
"""

from typing import Optional, List
from core.http_core.client import APIClient
from .models import (
    WeatherRequest, WeatherApiResponse, 
    get_weather_condition_description
)


class WeatherClient:
    """Open-Meteo Weather API Client"""
    
    def __init__(self):
        self.client = APIClient("https://api.open-meteo.com/v1")
    
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[WeatherApiResponse]:
        """
        Get current weather conditions
        
        Args:
            latitude: Location latitude in decimal degrees
            longitude: Location longitude in decimal degrees
            
        Returns:
            WeatherApiResponse entity or None
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True
        }
        
        data = self.client.get("/forecast", params=params)
        if data:
            return WeatherApiResponse.from_dict(data)
        return None
    
    def get_daily_forecast(self, latitude: float, longitude: float, 
                          forecast_days: int = 7) -> Optional[WeatherApiResponse]:
        """
        Get daily weather forecast
        
        Args:
            latitude: Location latitude in decimal degrees
            longitude: Location longitude in decimal degrees
            forecast_days: Number of forecast days (1-16, default 7)
            
        Returns:
            WeatherApiResponse entity or None
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": forecast_days,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,sunrise,sunset"
        }
        
        data = self.client.get("/forecast", params=params)
        if data:
            return WeatherApiResponse.from_dict(data)
        return None
    
    def get_hourly_forecast(self, latitude: float, longitude: float, 
                           forecast_days: int = 3) -> Optional[WeatherApiResponse]:
        """
        Get hourly weather forecast
        
        Args:
            latitude: Location latitude in decimal degrees
            longitude: Location longitude in decimal degrees
            forecast_days: Number of forecast days (1-16, default 3)
            
        Returns:
            WeatherApiResponse entity or None
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": forecast_days,
            "hourly": "temperature_2m,precipitation,weathercode,windspeed_10m"
        }
        
        data = self.client.get("/forecast", params=params)
        if data:
            return WeatherApiResponse.from_dict(data)
        return None
    
    def get_weather_forecast(self, latitude: float, longitude: float, 
                           forecast_days: int = 7,
                           daily_vars: Optional[List[str]] = None,
                           hourly_vars: Optional[List[str]] = None) -> Optional[WeatherApiResponse]:
        """
        Get custom weather forecast with specified variables
        
        Args:
            latitude: Location latitude in decimal degrees
            longitude: Location longitude in decimal degrees
            forecast_days: Number of forecast days (1-16)
            daily_vars: List of daily forecast variables
            hourly_vars: List of hourly forecast variables
            
        Returns:
            WeatherApiResponse entity or None
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
            return WeatherApiResponse.from_dict(data)
        return None
    
    def get_categories(self) -> List[str]:
        """
        Get available weather forecast categories
        
        Returns:
            List of forecast categories
        """
        return ["current", "daily", "hourly"]
    
    def get_available_daily_variables(self) -> List[str]:
        """
        Get available daily forecast variables
        
        Returns:
            List of daily variables
        """
        return [
            "temperature_2m_max", "temperature_2m_min", "precipitation_sum",
            "weathercode", "sunrise", "sunset", "windspeed_10m_max", 
            "windgusts_10m_max", "winddirection_10m_dominant"
        ]
    
    def get_available_hourly_variables(self) -> List[str]:
        """
        Get available hourly forecast variables
        
        Returns:
            List of hourly variables
        """
        return [
            "temperature_2m", "precipitation", "weathercode", "windspeed_10m",
            "winddirection_10m", "cloudcover", "pressure_msl", "surface_pressure"
        ] 