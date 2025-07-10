"""
天气API客户端
"""

from typing import Optional, List
from core.http_core.client import APIClient
from .models import WeatherRequest, WeatherResponse, weather_response_from_dict, get_weather_description


class WeatherClient:
    """Open-Meteo天气API客户端"""
    
    def __init__(self):
        self.client = APIClient("https://api.open-meteo.com/v1")
    
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[WeatherResponse]:
        """
        获取当前天气
        
        Args:
            latitude: 纬度
            longitude: 经度
            
        Returns:
            天气响应数据或None
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
        获取天气预报
        
        Args:
            latitude: 纬度
            longitude: 经度
            forecast_days: 预报天数
            daily_vars: 每日变量列表
            hourly_vars: 每小时变量列表
            
        Returns:
            天气响应数据或None
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
        获取每日天气预报
        
        Args:
            latitude: 纬度
            longitude: 经度
            forecast_days: 预报天数
            
        Returns:
            天气响应数据或None
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
        获取每小时天气预报
        
        Args:
            latitude: 纬度
            longitude: 经度
            forecast_days: 预报天数
            
        Returns:
            天气响应数据或None
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
        格式化当前天气信息
        
        Args:
            weather_response: 天气响应数据
            
        Returns:
            格式化的天气信息字符串
        """
        if not weather_response.current_weather:
            return "当前天气数据不可用"
        
        current = weather_response.current_weather
        description = get_weather_description(current.weathercode)
        day_night = "白天" if current.is_day else "夜间"
        
        return f"""
当前天气 ({weather_response.timezone}):
时间: {current.time}
天气: {description}
温度: {current.temperature}°C
风速: {current.windspeed} km/h
风向: {current.winddirection}°
时段: {day_night}
位置: {weather_response.latitude}, {weather_response.longitude}
海拔: {weather_response.elevation}m
        """.strip()
    
    def format_daily_forecast(self, weather_response: WeatherResponse) -> str:
        """
        格式化每日天气预报
        
        Args:
            weather_response: 天气响应数据
            
        Returns:
            格式化的预报信息字符串
        """
        if not weather_response.daily:
            return "每日天气预报数据不可用"
        
        daily = weather_response.daily
        forecast_lines = [f"每日天气预报 ({weather_response.timezone}):"]
        
        for i, date in enumerate(daily.time):
            line = f"日期: {date}"
            
            if daily.temperature_2m_max and daily.temperature_2m_min:
                line += f", 温度: {daily.temperature_2m_min[i]}°C - {daily.temperature_2m_max[i]}°C"
            
            if daily.precipitation_sum:
                line += f", 降水: {daily.precipitation_sum[i]}mm"
            
            if daily.weathercode:
                description = get_weather_description(daily.weathercode[i])
                line += f", 天气: {description}"
            
            if daily.sunrise and daily.sunset:
                line += f", 日出: {daily.sunrise[i]}, 日落: {daily.sunset[i]}"
            
            forecast_lines.append(line)
        
        return "\n".join(forecast_lines) 