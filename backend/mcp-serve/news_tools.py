"""
News Tools Module
Contains all news-related MCP tools

Author: Andrew Wang
"""

import json
from fastmcp import FastMCP
from remote_api.news import NewsClient
from remote_api.news.models import (
    NEWS_CATEGORIES, NEWS_LANGUAGES, NEWS_LOCALES,
    get_category_error_message, get_language_error_message, get_locale_error_message
)

from dotenv import load_dotenv
load_dotenv()

# Initialize news client
news_client = NewsClient()


def register_news_tools(mcp: FastMCP):
    """
    Register news tools to MCP instance
    
    Args:
        mcp: FastMCP instance
    """
    
    # Get news (top headlines or by category)
    @mcp.tool
    def get_news(language: str = "en", category: str = "", limit: int = 10) -> str:
        """
        Get news (top headlines or by category)
        
        Args:
            language: Language code (default "en")
                     Supported languages: ar (Arabic), bg (Bulgarian), bn (Bengali), cs (Czech), 
                     da (Danish), de (German), el (Greek), en (English), es (Spanish), et (Estonian), 
                     fa (Persian), fi (Finnish), fr (French), he (Hebrew), hi (Hindi), hr (Croatian), 
                     hu (Hungarian), id (Indonesian), it (Italian), ja (Japanese), ko (Korean), 
                     lt (Lithuanian), multi (Multiple languages), nl (Dutch), no (Norwegian), 
                     pl (Polish), pt (Portuguese), ro (Romanian), ru (Russian), sk (Slovak), 
                     sv (Swedish), ta (Tamil), th (Thai), tr (Turkish), uk (Ukrainian), 
                     vi (Vietnamese), zh (Chinese)
            category: News category (optional, leave empty for all news)
                     Supported categories: general, science, sports, business, health, entertainment, 
                     tech, politics, food, travel
            limit: Number of news items to return (default 10)
            
        Returns:
            JSON string of NewsApiResponse entity in format:
            {
                "meta": {
                    "found": 2847,
                    "returned": 10,
                    "limit": 10,
                    "page": 1
                },
                "data": [
                    {
                        "uuid": "3e3e3e3e-3e3e-3e3e-3e3e-3e3e3e3e3e3e",
                        "title": "Sample News Title",
                        "description": "Sample news description...",
                        "url": "https://example.com/news/sample",
                        "source": "Example News",
                        "published_at": "2025-01-18T10:30:00Z",
                        "language": "en",
                        "locale": "us",
                        "keywords": "keyword1, keyword2",
                        "snippet": "Sample snippet...",
                        "image_url": "https://example.com/image.jpg",
                        "categories": ["general"],
                        "relevance_score": 0.95
                    }
                ]
            }
        """
        try:
            # Get news
            category_param = category if category else None
            result = news_client.get_news(language, category_param, limit)
            
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": "Unable to get news"}, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": f"Error getting news: {str(e)}"}, ensure_ascii=False)

    # Get top news headlines
    @mcp.tool
    def get_top_news(locale: str = "us", category: str = "", limit: int = 10) -> str:
        """
        Get top news headlines
        
        Args:
            locale: Locale code (default "us")
                   Supported locales: us (United States), gb (United Kingdom), ca (Canada), 
                   au (Australia), in (India), jp (Japan), kr (South Korea), cn (China), 
                   de (Germany), fr (France), es (Spain), it (Italy), ru (Russia), 
                   br (Brazil), mx (Mexico)
            category: News category (optional, leave empty for all news)
                     Supported categories: general, science, sports, business, health, entertainment, 
                     tech, politics, food, travel
            limit: Number of news items to return (default 10)
            
        Returns:
            JSON string of NewsApiResponse entity in format:
            {
                "meta": {
                    "found": 2847,
                    "returned": 10,
                    "limit": 10,
                    "page": 1
                },
                "data": [
                    {
                        "uuid": "3e3e3e3e-3e3e-3e3e-3e3e-3e3e3e3e3e3e",
                        "title": "Top News Title",
                        "description": "Top news description...",
                        "url": "https://example.com/news/top",
                        "source": "Example News",
                        "published_at": "2025-01-18T10:30:00Z",
                        "language": "en",
                        "locale": "us",
                        "keywords": "keyword1, keyword2",
                        "snippet": "Top news snippet...",
                        "image_url": "https://example.com/image.jpg",
                        "categories": ["general"],
                        "relevance_score": 0.95
                    }
                ]
            }
        """
        try:
            # Get top news
            category_param = category if category else None
            result = news_client.get_top_news(locale, category_param, limit)
            
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": "Unable to get top news"}, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": f"Error getting top news: {str(e)}"}, ensure_ascii=False)

    # Search news
    @mcp.tool
    def search_news(query: str, language: str = "en", days_back: int = 7, limit: int = 10) -> str:
        """
        Search news by keywords
        
        Args:
            query: Search keywords (required)
            language: Language code (default "en")
                     Supported languages: ar (Arabic), bg (Bulgarian), bn (Bengali), cs (Czech), 
                     da (Danish), de (German), el (Greek), en (English), es (Spanish), et (Estonian), 
                     fa (Persian), fi (Finnish), fr (French), he (Hebrew), hi (Hindi), hr (Croatian), 
                     hu (Hungarian), id (Indonesian), it (Italian), ja (Japanese), ko (Korean), 
                     lt (Lithuanian), multi (Multiple languages), nl (Dutch), no (Norwegian), 
                     pl (Polish), pt (Portuguese), ro (Romanian), ru (Russian), sk (Slovak), 
                     sv (Swedish), ta (Tamil), th (Thai), tr (Turkish), uk (Ukrainian), 
                     vi (Vietnamese), zh (Chinese)
            days_back: Number of days to search back (default 7)
            limit: Number of news items to return (default 10)
            
        Returns:
            JSON string of NewsApiResponse entity in format:
            {
                "meta": {
                    "found": 156,
                    "returned": 10,
                    "limit": 10,
                    "page": 1
                },
                "data": [
                    {
                        "uuid": "4f4f4f4f-4f4f-4f4f-4f4f-4f4f4f4f4f4f",
                        "title": "Search Result Title",
                        "description": "Search result description...",
                        "url": "https://example.com/news/search-result",
                        "source": "Example News",
                        "published_at": "2025-01-18T09:15:00Z",
                        "language": "en",
                        "locale": "us",
                        "keywords": "search, keywords",
                        "snippet": "Search snippet...",
                        "image_url": "https://example.com/search-image.jpg",
                        "categories": ["general", "tech"],
                        "relevance_score": 0.87
                    }
                ]
            }
        """
        try:
            # Validate query
            if not query.strip():
                return json.dumps({"error": "Search query cannot be empty"}, ensure_ascii=False)
            
            # Search news
            result = news_client.search_news(query, language, days_back, limit)
            
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": f"No news found about '{query}'"}, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": f"Error searching news: {str(e)}"}, ensure_ascii=False)

    print("✅ News tools registered")