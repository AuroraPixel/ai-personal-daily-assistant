"""
Weather API Data Models

Author: Andrew Wang
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


class WeatherRequest(BaseModel):
    """Weather API request parameters"""
    latitude: float
    longitude: float
    current_weather: bool = True
    forecast_days: Optional[int] = None
    daily: Optional[List[str]] = None
    hourly: Optional[List[str]] = None


class CurrentWeatherData(BaseModel):
    """Current weather data (real-time conditions)"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    time: str                           # Current observation time (ISO8601)
    interval: Optional[int] = None      # Observation interval in seconds
    temperature: float                  # Temperature in Celsius
    windspeed: float                   # Wind speed in km/h  
    winddirection: int                 # Wind direction in degrees (0-360°)
    is_day: int                        # Daytime indicator (1=day, 0=night)
    weathercode: int                   # Weather condition code (WMO standard)


class CurrentWeatherUnits(BaseModel):
    """Current weather measurement units"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    time: str
    interval: str
    temperature: str
    windspeed: str
    winddirection: str
    is_day: str
    weathercode: str


class DailyForecastData(BaseModel):
    """Daily weather forecast data (multi-day predictions)"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    time: List[str]                                      # Forecast dates (ISO8601)
    temperature_2m_max: Optional[List[float]] = None     # Daily maximum temperature in Celsius
    temperature_2m_min: Optional[List[float]] = None     # Daily minimum temperature in Celsius
    precipitation_sum: Optional[List[float]] = None      # Total daily precipitation in mm
    weathercode: Optional[List[int]] = None              # Daily weather condition codes
    sunrise: Optional[List[str]] = None                  # Sunrise times (ISO8601)
    sunset: Optional[List[str]] = None                   # Sunset times (ISO8601)


class DailyForecastUnits(BaseModel):
    """Daily forecast measurement units"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    time: str
    temperature_2m_max: str
    temperature_2m_min: str
    precipitation_sum: str
    weathercode: str


class HourlyForecastData(BaseModel):
    """Hourly weather forecast data (detailed predictions)"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    time: List[str]                                  # Forecast hours (ISO8601)
    temperature_2m: Optional[List[float]] = None     # Hourly temperature in Celsius
    precipitation: Optional[List[float]] = None      # Hourly precipitation in mm
    weathercode: Optional[List[int]] = None          # Hourly weather condition codes
    windspeed_10m: Optional[List[float]] = None      # Hourly wind speed in km/h


class HourlyForecastUnits(BaseModel):
    """Hourly forecast measurement units"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    time: str
    temperature_2m: str
    precipitation: str
    weathercode: str
    windspeed_10m: str


class WeatherApiResponse(BaseModel):
    """Universal weather API response for all endpoints"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    # Basic response metadata
    latitude: float                              # Location latitude in decimal degrees
    longitude: float                             # Location longitude in decimal degrees
    generationtime_ms: float                     # API response generation time in milliseconds
    utc_offset_seconds: int                      # UTC offset in seconds
    timezone: str                                # Timezone identifier (e.g., "GMT", "Europe/London")
    timezone_abbreviation: str                   # Timezone abbreviation (e.g., "GMT", "CET")
    elevation: float                             # Location elevation in meters above sea level
    
    # Current weather (for current weather endpoint)
    current_weather_units: Optional[CurrentWeatherUnits] = None
    current_weather: Optional[CurrentWeatherData] = None
    
    # Daily forecast (for daily forecast endpoint) 
    daily_units: Optional[DailyForecastUnits] = None
    daily: Optional[DailyForecastData] = None
    
    # Hourly forecast (for hourly forecast endpoint)
    hourly_units: Optional[HourlyForecastUnits] = None
    hourly: Optional[HourlyForecastData] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeatherApiResponse":
        """Create WeatherApiResponse from dictionary using Pydantic's automatic mapping"""
        return cls(**data)


# Weather condition code mapping for easy understanding
WEATHER_CONDITION_DESCRIPTIONS = {
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


def get_weather_condition_description(weather_condition_code: int) -> str:
    """Get weather condition description based on weather condition code"""
    return WEATHER_CONDITION_DESCRIPTIONS.get(weather_condition_code, "Unknown weather condition") 