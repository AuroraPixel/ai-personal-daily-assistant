"""
天气API数据模型
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class WeatherRequest:
    """天气API请求参数"""
    latitude: float
    longitude: float
    current_weather: bool = True
    forecast_days: Optional[int] = None
    daily: Optional[List[str]] = None
    hourly: Optional[List[str]] = None


@dataclass
class CurrentWeather:
    """当前天气数据"""
    temperature: float
    windspeed: float
    winddirection: int
    weathercode: int
    is_day: int
    time: str


@dataclass
class DailyWeather:
    """每日天气数据"""
    time: List[str]
    temperature_2m_max: Optional[List[float]] = None
    temperature_2m_min: Optional[List[float]] = None
    precipitation_sum: Optional[List[float]] = None
    weathercode: Optional[List[int]] = None
    sunrise: Optional[List[str]] = None
    sunset: Optional[List[str]] = None


@dataclass
class HourlyWeather:
    """每小时天气数据"""
    time: List[str]
    temperature_2m: Optional[List[float]] = None
    precipitation: Optional[List[float]] = None
    weathercode: Optional[List[int]] = None
    windspeed_10m: Optional[List[float]] = None


@dataclass
class WeatherResponse:
    """天气API响应数据"""
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_weather: Optional[CurrentWeather] = None
    daily: Optional[DailyWeather] = None
    hourly: Optional[HourlyWeather] = None


# 天气代码映射
WEATHER_CODE_MAP = {
    0: "晴朗",
    1: "主要晴朗",
    2: "部分多云",
    3: "阴天",
    45: "雾",
    48: "沉积雾霾",
    51: "小雨",
    53: "中雨",
    55: "大雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    95: "雷暴",
    96: "轻雷暴伴冰雹",
    99: "重雷暴伴冰雹"
}


def get_weather_description(weather_code: int) -> str:
    """根据天气代码获取天气描述"""
    return WEATHER_CODE_MAP.get(weather_code, "未知天气")


def weather_response_from_dict(data: dict) -> WeatherResponse:
    """从API响应字典创建WeatherResponse对象"""
    current_weather = None
    if "current_weather" in data:
        cw_data = data["current_weather"]
        current_weather = CurrentWeather(
            temperature=cw_data["temperature"],
            windspeed=cw_data["windspeed"],
            winddirection=cw_data["winddirection"],
            weathercode=cw_data["weathercode"],
            is_day=cw_data["is_day"],
            time=cw_data["time"]
        )
    
    daily = None
    if "daily" in data:
        daily_data = data["daily"]
        daily = DailyWeather(
            time=daily_data["time"],
            temperature_2m_max=daily_data.get("temperature_2m_max"),
            temperature_2m_min=daily_data.get("temperature_2m_min"),
            precipitation_sum=daily_data.get("precipitation_sum"),
            weathercode=daily_data.get("weathercode"),
            sunrise=daily_data.get("sunrise"),
            sunset=daily_data.get("sunset")
        )
    
    hourly = None
    if "hourly" in data:
        hourly_data = data["hourly"]
        hourly = HourlyWeather(
            time=hourly_data["time"],
            temperature_2m=hourly_data.get("temperature_2m"),
            precipitation=hourly_data.get("precipitation"),
            weathercode=hourly_data.get("weathercode"),
            windspeed_10m=hourly_data.get("windspeed_10m")
        )
    
    return WeatherResponse(
        latitude=data["latitude"],
        longitude=data["longitude"],
        generationtime_ms=data["generationtime_ms"],
        utc_offset_seconds=data["utc_offset_seconds"],
        timezone=data["timezone"],
        timezone_abbreviation=data["timezone_abbreviation"],
        elevation=data["elevation"],
        current_weather=current_weather,
        daily=daily,
        hourly=hourly
    ) 