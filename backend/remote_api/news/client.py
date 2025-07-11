"""
News API Client

Author: Andrew Wang
"""
import os
import json
from typing import Optional, List
from datetime import datetime, timedelta
from core.http_core.client import APIClient
from .models import (
    NewsApiResponse, NewsArticle, NewsSearchRequest,
    format_news_article, format_news_list, get_category_display_name,
    get_locale_display_name, NEWS_CATEGORIES, NEWS_LOCALES, NEWS_LANGUAGES,
    validate_category, validate_language, validate_locale,
    get_category_error_message, get_language_error_message, get_locale_error_message
)


class NewsClient:
    """The News API Client"""
    
    def __init__(self):
        self.client = APIClient("https://api.thenewsapi.com/v1")
        # Get API token from environment variables
        self.api_token = os.getenv("NEWS_API_TOKEN")
        if not self.api_token:
            print("Warning: Environment variable NEWS_API_TOKEN not found, News API may not work properly")
    
    def _add_auth_params(self, params: dict) -> dict:
        """Add authentication information to request parameters"""
        if self.api_token:
            params["api_token"] = self.api_token
        return params
    
    def _debug_request(self, endpoint: str, params: dict):
        """Debug output request information"""
        print(f"Debug: Request endpoint {endpoint}")
        print(f"Debug: Request parameters {params}")
        if not self.api_token:
            print("Debug: API token not set")
    
    def get_news(self, language: str = "en", 
                 category: Optional[str] = None,
                 limit: int = 10) -> Optional[NewsApiResponse]:
        """
        Get news (top headlines or by category)
        
        Args:
            language: Language code (must be in supported languages list)
            category: News category (optional, must be in supported categories list)
            limit: Number of news items to return (default 10)
            
        Returns:
            NewsApiResponse or None if request failed
        """
        # Validate language
        if not validate_language(language):
            raise ValueError(get_language_error_message())
        
        # Validate category if provided
        if category and not validate_category(category):
            raise ValueError(get_category_error_message())
        
        params = {
            "language": language,
            "limit": limit
        }
        
        if category:
            params["categories"] = category
        
        # Add authentication parameters
        params = self._add_auth_params(params)
        
        data = self.client.get("/news/all", params=params)
        
        if data:
            return NewsApiResponse.from_dict(data)
        else:
            print("Note: News API request failed. Please check if API key is correct.")
            return None
    
    def search_news(self, query: str, 
                   language: str = "en",
                   days_back: int = 7,
                   limit: int = 10) -> Optional[NewsApiResponse]:
        """
        Search news
        
        Args:
            query: Search keywords
            language: Language code (must be in supported languages list)
            days_back: Number of days to search back (default 7)
            limit: Number of news items to return (default 10)
            
        Returns:
            NewsApiResponse or None if request failed
        """
        # Validate language
        if not validate_language(language):
            raise ValueError(get_language_error_message())
        
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
        
        # Add authentication parameters
        params = self._add_auth_params(params)
        
        data = self.client.get("/news/all", params=params)
        
        if data:
            return NewsApiResponse.from_dict(data)
        else:
            print("Note: News search request failed. Please check if API key is correct.")
            return None
    
    def get_available_categories(self) -> List[str]:
        """Get available news categories"""
        return NEWS_CATEGORIES.copy()
    
    def get_available_locales(self) -> List[str]:
        """Get available locale codes"""
        return NEWS_LOCALES.copy()
    
    def get_available_languages(self) -> List[str]:
        """Get available language codes"""
        return NEWS_LANGUAGES.copy()
    
    def format_headlines(self, response: NewsApiResponse) -> str:
        """
        Format headlines
        
        Args:
            response: News API response
            
        Returns:
            Formatted news string
        """
        if not response.data:
            return "No related news found"
        
        header = f"Top Headlines (Found {response.meta.found}, showing {response.meta.returned}):\n"
        return header + format_news_list(response.data)
    
    def format_search_results(self, response: NewsApiResponse, query: str) -> str:
        """
        Format search results
        
        Args:
            response: News API response
            query: Search keywords
            
        Returns:
            Formatted search results string
        """
        if not response.data:
            return f"No news found related to '{query}'"
        
        header = f"Search results for '{query}' (Found {response.meta.found}, showing {response.meta.returned}):\n"
        return header + format_news_list(response.data)
    
    def format_category_news(self, response: NewsApiResponse, category: str) -> str:
        """
        Format category news
        
        Args:
            response: News API response
            category: Category
            
        Returns:
            Formatted category news string
        """
        if not response.data:
            return f"No {get_category_display_name(category)} news found"
        
        category_name = get_category_display_name(category)
        header = f"{category_name} News (Found {response.meta.found}, showing {response.meta.returned}):\n"
        return header + format_news_list(response.data)
    
    def get_article_details(self, article: NewsArticle) -> str:
        """
        Get article details
        
        Args:
            article: News article
            
        Returns:
            Formatted article details
        """
        return format_news_article(article) 