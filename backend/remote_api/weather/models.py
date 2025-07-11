"""
Weather API Data Models

Author: Andrew Wang
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class WeatherRequest:
    """Weather API request parameters"""
    latitude: float
    longitude: float
    current_weather: bool = True
    forecast_days: Optional[int] = None
    daily: Optional[List[str]] = None
    hourly: Optional[List[str]] = None


@dataclass
class CurrentWeather:
    """Current weather data"""
    temperature: float
    windspeed: float
    winddirection: int
    weathercode: int
    is_day: int
    time: str


@dataclass
class DailyWeather:
    """Daily weather data"""
    time: List[str]
    temperature_2m_max: Optional[List[float]] = None
    temperature_2m_min: Optional[List[float]] = None
    precipitation_sum: Optional[List[float]] = None
    weathercode: Optional[List[int]] = None
    sunrise: Optional[List[str]] = None
    sunset: Optional[List[str]] = None


@dataclass
class HourlyWeather:
    """Hourly weather data"""
    time: List[str]
    temperature_2m: Optional[List[float]] = None
    precipitation: Optional[List[float]] = None
    weathercode: Optional[List[int]] = None
    windspeed_10m: Optional[List[float]] = None


@dataclass
class WeatherResponse:
    """Weather API response data"""
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


# Weather code mapping
WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


def get_weather_description(weather_code: int) -> str:
    """Get weather description based on weather code"""
    return WEATHER_CODE_MAP.get(weather_code, "Unknown weather")


def weather_response_from_dict(data: dict) -> WeatherResponse:
    """Create WeatherResponse object from API response dictionary"""
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