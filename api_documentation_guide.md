# API Documentation Guide: Free APIs for Personal Daily Assistant

## Overview

This guide provides comprehensive documentation for all the free APIs used in the Personal Daily Assistant project. All APIs listed here are completely free to use, require no API keys for basic functionality, and are suitable for development and demonstration purposes.

## Weather API: Open-Meteo

### API Overview
Open-Meteo is a free, open-source weather API that provides global weather data without requiring API keys or registration. The API offers current weather conditions, forecasts, and historical weather data with high accuracy and reliability.

**Base URL**: `https://api.open-meteo.com/v1/`  
**Documentation**: https://open-meteo.com/en/docs  
**Rate Limits**: No strict limits for reasonable usage  
**Authentication**: None required

### Current Weather Endpoint

**Endpoint**: `GET /forecast`

**Required Parameters**:
- `latitude`: Latitude coordinate (decimal degrees)
- `longitude`: Longitude coordinate (decimal degrees)
- `current_weather`: Set to `true` to get current conditions

**Example Request**:
```
https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current_weather=true
```

**Example Response**:
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "generationtime_ms": 0.123,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "timezone_abbreviation": "GMT",
  "elevation": 10.0,
  "current_weather": {
    "temperature": 22.5,
    "windspeed": 8.2,
    "winddirection": 180,
    "weathercode": 3,
    "is_day": 1,
    "time": "2024-01-15T15:00"
  }
}
```

### Weather Forecast Endpoint

**Additional Parameters for Forecasts**:
- `daily`: Comma-separated list of daily variables
- `hourly`: Comma-separated list of hourly variables
- `forecast_days`: Number of forecast days (1-16)

**Common Daily Variables**:
- `temperature_2m_max`: Maximum daily temperature
- `temperature_2m_min`: Minimum daily temperature
- `precipitation_sum`: Total daily precipitation
- `weathercode`: Weather condition code
- `sunrise`: Sunrise time
- `sunset`: Sunset time

**Example Forecast Request**:
```
https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode&forecast_days=7
```

### Weather Codes Reference

| Code | Condition |
|------|-----------|
| 0 | Clear sky |
| 1, 2, 3 | Mainly clear, partly cloudy, overcast |
| 45, 48 | Fog and depositing rime fog |
| 51, 53, 55 | Drizzle: Light, moderate, dense |
| 61, 63, 65 | Rain: Slight, moderate, heavy |
| 71, 73, 75 | Snow fall: Slight, moderate, heavy |
| 95, 96, 99 | Thunderstorm |

### Implementation Example

```python
import requests

def get_current_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["current_weather"]
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

# Usage
weather = get_current_weather(40.7128, -74.0060)
if weather:
    print(f"Temperature: {weather['temperature']}°C")
    print(f"Weather Code: {weather['weathercode']}")
```

## Recipe API: TheMealDB

### API Overview
TheMealDB is a free recipe database with a JSON API that provides access to thousands of recipes from around the world. The API includes detailed recipe information, ingredients, instructions, and images.

**Base URL**: `https://www.themealdb.com/api/json/v1/1/`  
**Documentation**: https://www.themealdb.com/api.php  
**Rate Limits**: No strict limits for reasonable usage  
**Authentication**: None required

### Search Recipes by Name

**Endpoint**: `GET /search.php`

**Parameters**:
- `s`: Search term for recipe name

**Example Request**:
```
https://www.themealdb.com/api/json/v1/1/search.php?s=chicken
```

**Example Response**:
```json
{
  "meals": [
    {
      "idMeal": "52940",
      "strMeal": "Brown Stew Chicken",
      "strDrinkAlternate": null,
      "strCategory": "Chicken",
      "strArea": "Jamaican",
      "strInstructions": "Squeeze lime over chicken and rub well...",
      "strMealThumb": "https://www.themealdb.com/images/media/meals/sypxpx1515365095.jpg",
      "strTags": "Stew",
      "strYoutube": "https://www.youtube.com/watch?v=_gDXKaNHjzA",
      "strIngredient1": "Chicken",
      "strMeasure1": "1 whole",
      "strIngredient2": "Tomato",
      "strMeasure2": "1 chopped"
    }
  ]
}
```

### Search by Main Ingredient

**Endpoint**: `GET /filter.php`

**Parameters**:
- `i`: Main ingredient name

**Example Request**:
```
https://www.themealdb.com/api/json/v1/1/filter.php?i=chicken_breast
```

### Browse by Category

**Endpoint**: `GET /filter.php`

**Parameters**:
- `c`: Category name

**Available Categories**: Beef, Breakfast, Chicken, Dessert, Goat, Lamb, Miscellaneous, Pasta, Pork, Seafood, Side, Starter, Vegan, Vegetarian

**Example Request**:
```
https://www.themealdb.com/api/json/v1/1/filter.php?c=Vegetarian
```

### Browse by Area/Cuisine

**Endpoint**: `GET /filter.php`

**Parameters**:
- `a`: Area/cuisine name

**Available Areas**: American, British, Canadian, Chinese, Croatian, Dutch, Egyptian, French, Greek, Indian, Irish, Italian, Jamaican, Japanese, Kenyan, Malaysian, Mexican, Moroccan, Polish, Portuguese, Russian, Spanish, Thai, Tunisian, Turkish, Vietnamese

**Example Request**:
```
https://www.themealdb.com/api/json/v1/1/filter.php?a=Italian
```

### Get Recipe Details

**Endpoint**: `GET /lookup.php`

**Parameters**:
- `i`: Meal ID

**Example Request**:
```
https://www.themealdb.com/api/json/v1/1/lookup.php?i=52940
```

### Random Recipe

**Endpoint**: `GET /random.php`

**Example Request**:
```
https://www.themealdb.com/api/json/v1/1/random.php
```

### Implementation Example

```python
import requests

class RecipeAPI:
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    
    def search_by_name(self, name):
        url = f"{self.BASE_URL}/search.php"
        params = {"s": name}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("meals", [])
        except requests.RequestException as e:
            print(f"Error searching recipes: {e}")
            return []
    
    def search_by_ingredient(self, ingredient):
        url = f"{self.BASE_URL}/filter.php"
        params = {"i": ingredient}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("meals", [])
        except requests.RequestException as e:
            print(f"Error searching by ingredient: {e}")
            return []
    
    def get_recipe_details(self, meal_id):
        url = f"{self.BASE_URL}/lookup.php"
        params = {"i": meal_id}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            meals = data.get("meals", [])
            return meals[0] if meals else None
        except requests.RequestException as e:
            print(f"Error getting recipe details: {e}")
            return None

# Usage
recipe_api = RecipeAPI()
recipes = recipe_api.search_by_name("pasta")
for recipe in recipes[:3]:  # Show first 3 results
    print(f"Recipe: {recipe['strMeal']}")
    print(f"Category: {recipe['strCategory']}")
    print(f"Area: {recipe['strArea']}")
```

## News API: The News API

### API Overview
The News API provides free access to news articles from various sources worldwide. It offers current news, top headlines, and search capabilities across different categories and languages.

**Base URL**: `https://api.thenewsapi.com/v1/`  
**Documentation**: https://www.thenewsapi.com/documentation  
**Rate Limits**: 100 requests per day for free tier  
**Authentication**: None required for basic usage

### Top Headlines

**Endpoint**: `GET /news/top`

**Parameters**:
- `locale`: Language/country code (e.g., 'us', 'gb', 'ca')
- `limit`: Number of articles to return (max 50)

**Example Request**:
```
https://api.thenewsapi.com/v1/news/top?locale=us&limit=10
```

**Example Response**:
```json
{
  "meta": {
    "found": 50,
    "returned": 10,
    "limit": 10,
    "page": 1
  },
  "data": [
    {
      "uuid": "12345678-1234-1234-1234-123456789012",
      "title": "Breaking News: Important Event Happens",
      "description": "This is a description of the news article...",
      "keywords": "news, breaking, important",
      "snippet": "Short snippet of the article content...",
      "url": "https://example.com/news/article",
      "image_url": "https://example.com/image.jpg",
      "language": "en",
      "published_at": "2024-01-15T10:30:00.000000Z",
      "source": "Example News",
      "categories": ["general"],
      "relevance_score": null,
      "locale": "us"
    }
  ]
}
```

### Search News

**Endpoint**: `GET /news/all`

**Parameters**:
- `search`: Search query
- `language`: Language code (e.g., 'en', 'es', 'fr')
- `published_after`: Date filter (YYYY-MM-DD format)
- `published_before`: Date filter (YYYY-MM-DD format)
- `limit`: Number of articles (max 50)

**Example Request**:
```
https://api.thenewsapi.com/v1/news/all?search=technology&language=en&limit=5
```

### Categories

**Endpoint**: `GET /news/top`

**Available Categories**:
- general
- business
- entertainment
- health
- science
- sports
- technology

**Example Request**:
```
https://api.thenewsapi.com/v1/news/top?locale=us&categories=technology&limit=10
```

### Implementation Example

```python
import requests
from datetime import datetime, timedelta

class NewsAPI:
    BASE_URL = "https://api.thenewsapi.com/v1"
    
    def get_top_headlines(self, locale="us", limit=10):
        url = f"{self.BASE_URL}/news/top"
        params = {
            "locale": locale,
            "limit": limit
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.RequestException as e:
            print(f"Error fetching top headlines: {e}")
            return []
    
    def search_news(self, query, language="en", days_back=7, limit=10):
        url = f"{self.BASE_URL}/news/all"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        params = {
            "search": query,
            "language": language,
            "published_after": start_date.strftime("%Y-%m-%d"),
            "published_before": end_date.strftime("%Y-%m-%d"),
            "limit": limit
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.RequestException as e:
            print(f"Error searching news: {e}")
            return []
    
    def get_category_news(self, category, locale="us", limit=10):
        url = f"{self.BASE_URL}/news/top"
        params = {
            "locale": locale,
            "categories": category,
            "limit": limit
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.RequestException as e:
            print(f"Error fetching category news: {e}")
            return []

# Usage
news_api = NewsAPI()

# Get top headlines
headlines = news_api.get_top_headlines(limit=5)
for article in headlines:
    print(f"Title: {article['title']}")
    print(f"Source: {article['source']}")
    print(f"Published: {article['published_at']}")
    print("---")

# Search for specific topics
tech_news = news_api.search_news("artificial intelligence", limit=3)
for article in tech_news:
    print(f"Title: {article['title']}")
    print(f"Description: {article['description']}")
```

## Development/Testing API: JSONPlaceholder

### API Overview
JSONPlaceholder is a free fake REST API for testing and prototyping. It provides realistic data for users, posts, comments, albums, photos, and todos that can be used for development and demonstration purposes.

**Base URL**: `https://jsonplaceholder.typicode.com/`  
**Documentation**: https://jsonplaceholder.typicode.com/guide/  
**Rate Limits**: No strict limits  
**Authentication**: None required

### Available Resources

**Users**: `/users` - User profiles and contact information  
**Posts**: `/posts` - Blog posts and articles  
**Comments**: `/comments` - Comments on posts  
**Albums**: `/albums` - Photo albums  
**Photos**: `/photos` - Individual photos  
**Todos**: `/todos` - Todo items and tasks

### Users Endpoint

**Endpoint**: `GET /users`

**Example Request**:
```
https://jsonplaceholder.typicode.com/users
```

**Example Response**:
```json
[
  {
    "id": 1,
    "name": "Leanne Graham",
    "username": "Bret",
    "email": "Sincere@april.biz",
    "address": {
      "street": "Kulas Light",
      "suite": "Apt. 556",
      "city": "Gwenborough",
      "zipcode": "92998-3874",
      "geo": {
        "lat": "-37.3159",
        "lng": "81.1496"
      }
    },
    "phone": "1-770-736-8031 x56442",
    "website": "hildegard.org",
    "company": {
      "name": "Romaguera-Crona",
      "catchPhrase": "Multi-layered client-server neural-net",
      "bs": "harness real-time e-markets"
    }
  }
]
```

### Posts Endpoint

**Endpoint**: `GET /posts`

**Filter by User**: `GET /posts?userId=1`

**Example Request**:
```
https://jsonplaceholder.typicode.com/posts?userId=1
```

### Comments Endpoint

**Endpoint**: `GET /comments`

**Filter by Post**: `GET /comments?postId=1`

### Todos Endpoint

**Endpoint**: `GET /todos`

**Filter by User**: `GET /todos?userId=1`

**Example Response**:
```json
[
  {
    "userId": 1,
    "id": 1,
    "title": "delectus aut autem",
    "completed": false
  }
]
```

### Implementation Example

```python
import requests

class JSONPlaceholderAPI:
    BASE_URL = "https://jsonplaceholder.typicode.com"
    
    def get_users(self):
        url = f"{self.BASE_URL}/users"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching users: {e}")
            return []
    
    def get_user_posts(self, user_id):
        url = f"{self.BASE_URL}/posts"
        params = {"userId": user_id}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching user posts: {e}")
            return []
    
    def get_user_todos(self, user_id):
        url = f"{self.BASE_URL}/todos"
        params = {"userId": user_id}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching user todos: {e}")
            return []

# Usage
api = JSONPlaceholderAPI()

# Get all users
users = api.get_users()
print(f"Found {len(users)} users")

# Get posts for first user
if users:
    user_posts = api.get_user_posts(users[0]["id"])
    print(f"User {users[0]['name']} has {len(user_posts)} posts")
```

## Error Handling Best Practices

### Common Error Scenarios

**Network Errors**: Handle connection timeouts, DNS resolution failures, and network interruptions gracefully.

**API Rate Limits**: Implement retry logic with exponential backoff for rate-limited requests.

**Invalid Responses**: Validate API responses and handle malformed JSON or unexpected data structures.

**Service Unavailability**: Implement fallback mechanisms when APIs are temporarily unavailable.

### Example Error Handling

```python
import requests
import time
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None, 
                    max_retries: int = 3) -> Optional[Dict[Any, Any]]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url, 
                    params=params, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # Validate JSON response
                try:
                    return response.json()
                except ValueError as e:
                    print(f"Invalid JSON response: {e}")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except requests.exceptions.ConnectionError:
                print(f"Connection error (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limited
                    print(f"Rate limited (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(5)  # Wait longer for rate limits
                else:
                    print(f"HTTP error {e.response.status_code}: {e}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                return None
        
        print(f"Failed to get response after {max_retries} attempts")
        return None
```

## Testing and Development Tips

### API Testing Tools

**Postman**: Use Postman collections to test API endpoints and save example requests.

**curl**: Command-line testing for quick API verification:
```bash
# Test weather API
curl "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current_weather=true"

# Test recipe API
curl "https://www.themealdb.com/api/json/v1/1/search.php?s=pasta"

# Test news API
curl "https://api.thenewsapi.com/v1/news/top?locale=us&limit=5"
```

### Development Environment Setup

**Environment Variables**: Store API configurations in environment variables:
```python
import os

# API configurations
WEATHER_API_BASE = os.getenv("WEATHER_API_BASE", "https://api.open-meteo.com/v1")
RECIPE_API_BASE = os.getenv("RECIPE_API_BASE", "https://www.themealdb.com/api/json/v1/1")
NEWS_API_BASE = os.getenv("NEWS_API_BASE", "https://api.thenewsapi.com/v1")
```

**Caching**: Implement caching to reduce API calls during development:
```python
import requests_cache

# Create cached session
session = requests_cache.CachedSession('api_cache', expire_after=300)

# Use cached session for requests
response = session.get(url, params=params)
```

### Mock Data for Testing

When APIs are unavailable, use mock data that matches the expected response format:

```python
# Mock weather data
MOCK_WEATHER = {
    "current_weather": {
        "temperature": 22.5,
        "windspeed": 8.2,
        "winddirection": 180,
        "weathercode": 3,
        "is_day": 1,
        "time": "2024-01-15T15:00"
    }
}

# Mock recipe data
MOCK_RECIPES = {
    "meals": [
        {
            "idMeal": "52940",
            "strMeal": "Test Recipe",
            "strCategory": "Chicken",
            "strArea": "American",
            "strInstructions": "Test cooking instructions...",
            "strMealThumb": "https://example.com/image.jpg"
        }
    ]
}
```

This comprehensive API documentation provides all the information needed to successfully integrate these free APIs into your Personal Daily Assistant project. Each API is well-documented, reliable, and suitable for both development and demonstration purposes.

