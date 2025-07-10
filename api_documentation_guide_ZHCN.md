# API文档指南：个人日常助手的免费API

## 概述

本指南为个人日常助手项目中使用的所有免费API提供全面的文档。这里列出的所有API都是完全免费使用的，基本功能无需API密钥，适合开发和演示目的。

## 天气API：Open-Meteo

### API概述
Open-Meteo是一个免费的开源天气API，提供全球天气数据，无需API密钥或注册。该API提供当前天气状况、预报和历史天气数据，具有高准确性和可靠性。

**基础URL**：`https://api.open-meteo.com/v1/`  
**文档**：https://open-meteo.com/en/docs  
**限制**：合理使用无严格限制  
**认证**：无需认证

### 当前天气接口

**接口**：`GET /forecast`

**必需参数**：
- `latitude`：纬度坐标（十进制度数）
- `longitude`：经度坐标（十进制度数）
- `current_weather`：设置为`true`以获取当前状况

**请求示例**：
```
https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current_weather=true
```

**响应示例**：
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

### 天气预报接口

**预报的额外参数**：
- `daily`：逗号分隔的日期变量列表
- `hourly`：逗号分隔的小时变量列表
- `forecast_days`：预报天数（1-16）

**常用日期变量**：
- `temperature_2m_max`：日最高温度
- `temperature_2m_min`：日最低温度
- `precipitation_sum`：日总降水量
- `weathercode`：天气状况代码
- `sunrise`：日出时间
- `sunset`：日落时间

**预报请求示例**：
```
https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode&forecast_days=7
```

### 天气代码参考

| 代码 | 状况 |
|------|-----------|
| 0 | 晴朗天空 |
| 1, 2, 3 | 主要晴朗、部分多云、阴天 |
| 45, 48 | 雾和沉积雾凇 |
| 51, 53, 55 | 毛毛雨：轻、中、重 |
| 61, 63, 65 | 雨：小、中、大 |
| 71, 73, 75 | 降雪：小、中、大 |
| 95, 96, 99 | 雷暴 |

### 实现示例

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
        print(f"获取天气数据时出错: {e}")
        return None

# 使用方法
weather = get_current_weather(40.7128, -74.0060)
if weather:
    print(f"温度: {weather['temperature']}°C")
    print(f"天气代码: {weather['weathercode']}")
```

## 食谱API：TheMealDB

### API概述
TheMealDB是一个免费的食谱数据库，提供JSON API访问来自世界各地的数千种食谱。该API包含详细的食谱信息、配料、说明和图片。

**基础URL**：`https://www.themealdb.com/api/json/v1/1/`  
**文档**：https://www.themealdb.com/api.php  
**限制**：合理使用无严格限制  
**认证**：无需认证

### 按名称搜索食谱

**接口**：`GET /search.php`

**参数**：
- `s`：食谱名称搜索词

**请求示例**：
```
https://www.themealdb.com/api/json/v1/1/search.php?s=chicken
```

**响应示例**：
```json
{
  "meals": [
    {
      "idMeal": "52940",
      "strMeal": "褐烧鸡肉",
      "strDrinkAlternate": null,
      "strCategory": "鸡肉",
      "strArea": "牙买加",
      "strInstructions": "在鸡肉上挤柠檬并充分揉搓...",
      "strMealThumb": "https://www.themealdb.com/images/media/meals/sypxpx1515365095.jpg",
      "strTags": "炖菜",
      "strYoutube": "https://www.youtube.com/watch?v=_gDXKaNHjzA",
      "strIngredient1": "鸡肉",
      "strMeasure1": "1整只",
      "strIngredient2": "番茄",
      "strMeasure2": "1个切碎"
    }
  ]
}
```

### 按主要配料搜索

**接口**：`GET /filter.php`

**参数**：
- `i`：主要配料名称

**请求示例**：
```
https://www.themealdb.com/api/json/v1/1/filter.php?i=chicken_breast
```

### 按类别浏览

**接口**：`GET /filter.php`

**参数**：
- `c`：类别名称

**可用类别**：牛肉、早餐、鸡肉、甜点、山羊肉、羊肉、杂项、意面、猪肉、海鲜、配菜、开胃菜、素食、纯素食

**请求示例**：
```
https://www.themealdb.com/api/json/v1/1/filter.php?c=Vegetarian
```

### 按地区/菜系浏览

**接口**：`GET /filter.php`

**参数**：
- `a`：地区/菜系名称

**可用地区**：美式、英式、加拿大、中式、克罗地亚、荷兰、埃及、法式、希腊、印度、爱尔兰、意大利、牙买加、日式、肯尼亚、马来西亚、墨西哥、摩洛哥、波兰、葡萄牙、俄式、西班牙、泰式、突尼斯、土耳其、越南

**请求示例**：
```
https://www.themealdb.com/api/json/v1/1/filter.php?a=Italian
```

### 获取食谱详情

**接口**：`GET /lookup.php`

**参数**：
- `i`：食谱ID

**请求示例**：
```
https://www.themealdb.com/api/json/v1/1/lookup.php?i=52940
```

### 随机食谱

**接口**：`GET /random.php`

**请求示例**：
```
https://www.themealdb.com/api/json/v1/1/random.php
```

### 实现示例

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
            print(f"搜索食谱时出错: {e}")
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
            print(f"按配料搜索时出错: {e}")
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
            print(f"获取食谱详情时出错: {e}")
            return None

# 使用方法
recipe_api = RecipeAPI()
recipes = recipe_api.search_by_name("pasta")
for recipe in recipes[:3]:  # 显示前3个结果
    print(f"食谱: {recipe['strMeal']}")
    print(f"类别: {recipe['strCategory']}")
    print(f"地区: {recipe['strArea']}")
```

## 新闻API：The News API

### API概述
The News API提供免费访问来自全球各种来源的新闻文章。它提供当前新闻、头条新闻和跨不同类别和语言的搜索功能。

**基础URL**：`https://api.thenewsapi.com/v1/`  
**文档**：https://www.thenewsapi.com/documentation  
**限制**：免费版每天100次请求  
**认证**：基本使用无需认证

### 头条新闻

**接口**：`GET /news/top`

**参数**：
- `locale`：语言/国家代码（如'us'、'gb'、'ca'）
- `limit`：返回文章数量（最多50）

**请求示例**：
```
https://api.thenewsapi.com/v1/news/top?locale=us&limit=10
```

**响应示例**：
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
      "title": "突发新闻：重要事件发生",
      "description": "这是新闻文章的描述...",
      "keywords": "新闻, 突发, 重要",
      "snippet": "文章内容的简短摘要...",
      "url": "https://example.com/news/article",
      "image_url": "https://example.com/image.jpg",
      "language": "en",
      "published_at": "2024-01-15T10:30:00.000000Z",
      "source": "示例新闻",
      "categories": ["general"],
      "relevance_score": null,
      "locale": "us"
    }
  ]
}
```

### 搜索新闻

**接口**：`GET /news/all`

**参数**：
- `search`：搜索查询
- `language`：语言代码（如'en'、'es'、'fr'）
- `published_after`：日期过滤器（YYYY-MM-DD格式）
- `published_before`：日期过滤器（YYYY-MM-DD格式）
- `limit`：文章数量（最多50）

**请求示例**：
```
https://api.thenewsapi.com/v1/news/all?search=technology&language=en&limit=5
```

### 类别

**接口**：`GET /news/top`

**可用类别**：
- general（综合）
- business（商业）
- entertainment（娱乐）
- health（健康）
- science（科学）
- sports（体育）
- technology（技术）

**请求示例**：
```
https://api.thenewsapi.com/v1/news/top?locale=us&categories=technology&limit=10
```

### 实现示例

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
            print(f"获取头条新闻时出错: {e}")
            return []
    
    def search_news(self, query, language="en", days_back=7, limit=10):
        url = f"{self.BASE_URL}/news/all"
        
        # 计算日期范围
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
            print(f"搜索新闻时出错: {e}")
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
            print(f"获取类别新闻时出错: {e}")
            return []

# 使用方法
news_api = NewsAPI()

# 获取头条新闻
headlines = news_api.get_top_headlines(limit=5)
for article in headlines:
    print(f"标题: {article['title']}")
    print(f"来源: {article['source']}")
    print(f"发布时间: {article['published_at']}")
    print("---")

# 搜索特定主题
tech_news = news_api.search_news("artificial intelligence", limit=3)
for article in tech_news:
    print(f"标题: {article['title']}")
    print(f"描述: {article['description']}")
```

## 开发/测试API：JSONPlaceholder

### API概述
JSONPlaceholder是一个免费的虚假REST API，用于测试和原型制作。它提供用户、帖子、评论、相册、照片和待办事项的真实数据，可用于开发和演示目的。

**基础URL**：`https://jsonplaceholder.typicode.com/`  
**文档**：https://jsonplaceholder.typicode.com/guide/  
**限制**：无严格限制  
**认证**：无需认证

### 可用资源

**用户**：`/users` - 用户资料和联系信息  
**帖子**：`/posts` - 博客帖子和文章  
**评论**：`/comments` - 帖子评论  
**相册**：`/albums` - 照片相册  
**照片**：`/photos` - 单张照片  
**待办事项**：`/todos` - 待办事项和任务

### 用户接口

**接口**：`GET /users`

**请求示例**：
```
https://jsonplaceholder.typicode.com/users
```

**响应示例**：
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
      "catchPhrase": "多层客户端-服务器神经网络",
      "bs": "利用实时电子市场"
    }
  }
]
```

### 帖子接口

**接口**：`GET /posts`

**按用户过滤**：`GET /posts?userId=1`

**请求示例**：
```
https://jsonplaceholder.typicode.com/posts?userId=1
```

### 评论接口

**接口**：`GET /comments`

**按帖子过滤**：`GET /comments?postId=1`

### 待办事项接口

**接口**：`GET /todos`

**按用户过滤**：`GET /todos?userId=1`

**响应示例**：
```json
[
  {
    "userId": 1,
    "id": 1,
    "title": "选择或自动",
    "completed": false
  }
]
```

### 实现示例

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
            print(f"获取用户时出错: {e}")
            return []
    
    def get_user_posts(self, user_id):
        url = f"{self.BASE_URL}/posts"
        params = {"userId": user_id}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取用户帖子时出错: {e}")
            return []
    
    def get_user_todos(self, user_id):
        url = f"{self.BASE_URL}/todos"
        params = {"userId": user_id}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取用户待办事项时出错: {e}")
            return []

# 使用方法
api = JSONPlaceholderAPI()

# 获取所有用户
users = api.get_users()
print(f"找到 {len(users)} 个用户")

# 获取第一个用户的帖子
if users:
    user_posts = api.get_user_posts(users[0]["id"])
    print(f"用户 {users[0]['name']} 有 {len(user_posts)} 个帖子")
```

## 错误处理最佳实践

### 常见错误情况

**网络错误**：优雅地处理连接超时、DNS解析失败和网络中断。

**API限制**：为受限制的请求实现指数退避的重试逻辑。

**无效响应**：验证API响应并处理格式错误的JSON或意外的数据结构。

**服务不可用**：当API临时不可用时实现回退机制。

### 错误处理示例

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
                
                # 验证JSON响应
                try:
                    return response.json()
                except ValueError as e:
                    print(f"无效的JSON响应: {e}")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    
            except requests.exceptions.ConnectionError:
                print(f"连接错误 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # 限制频率
                    print(f"频率限制 (尝试 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(5)  # 频率限制等待更长时间
                else:
                    print(f"HTTP错误 {e.response.status_code}: {e}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"请求错误: {e}")
                return None
        
        print(f"在 {max_retries} 次尝试后获取响应失败")
        return None
```

## 测试和开发技巧

### API测试工具

**Postman**：使用Postman集合测试API接口并保存示例请求。

**curl**：命令行测试快速API验证：
```bash
# 测试天气API
curl "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current_weather=true"

# 测试食谱API
curl "https://www.themealdb.com/api/json/v1/1/search.php?s=pasta"

# 测试新闻API
curl "https://api.thenewsapi.com/v1/news/top?locale=us&limit=5"
```

### 开发环境设置

**环境变量**：在环境变量中存储API配置：
```python
import os

# API配置
WEATHER_API_BASE = os.getenv("WEATHER_API_BASE", "https://api.open-meteo.com/v1")
RECIPE_API_BASE = os.getenv("RECIPE_API_BASE", "https://www.themealdb.com/api/json/v1/1")
NEWS_API_BASE = os.getenv("NEWS_API_BASE", "https://api.thenewsapi.com/v1")
```

**缓存**：实现缓存以减少开发期间的API调用：
```python
import requests_cache

# 创建缓存会话
session = requests_cache.CachedSession('api_cache', expire_after=300)

# 使用缓存会话进行请求
response = session.get(url, params=params)
```

### 测试用模拟数据

当API不可用时，使用与预期响应格式匹配的模拟数据：

```python
# 模拟天气数据
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

# 模拟食谱数据
MOCK_RECIPES = {
    "meals": [
        {
            "idMeal": "52940",
            "strMeal": "测试食谱",
            "strCategory": "鸡肉",
            "strArea": "美式",
            "strInstructions": "测试烹饪说明...",
            "strMealThumb": "https://example.com/image.jpg"
        }
    ]
}
```

这份全面的API文档提供了成功将这些免费API集成到您的个人日常助手项目中所需的所有信息。每个API都有良好的文档、可靠性，适合开发和演示目的。 