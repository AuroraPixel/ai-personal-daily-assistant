"""
News API Client

Author: Andrew Wang
"""
import os
from typing import Optional, List
from datetime import datetime, timedelta
from core.http_core.client import APIClient
from .models import (
    NewsResponse, NewsArticle, NewsSearchRequest,
    news_response_from_dict, format_news_article,
    format_news_list, get_category_display_name,
    get_locale_display_name,
    NEWS_CATEGORIES, NEWS_LOCALES, NEWS_LANGUAGES
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
    
    def get_top_headlines(self, language: str = "en", 
                         category: Optional[str] = None,
                         limit: int = 10) -> Optional[NewsResponse]:
        """
        Get top headlines
        
        Args:
            language: Language code
            category: News category
            limit: Number of news items to return
            
        Returns:
            News response or None
        """
        params = {
            "language": language,
            "limit": limit
        }
        
        if category:
            if category not in NEWS_CATEGORIES:
                print(f"Invalid category: {category}. Available categories: {NEWS_CATEGORIES}")
                return None
            params["categories"] = category
        
        # Add authentication parameters
        params = self._add_auth_params(params)
        
        data = self.client.get("/news/all", params=params)
        
        if data:
            return news_response_from_dict(data)
        else:
            print("Note: News API request failed. Please check if API key is correct.")
            return None
    
    def search_news(self, query: str, 
                   language: str = "en",
                   days_back: int = 7,
                   limit: int = 10) -> Optional[NewsResponse]:
        """
        Search news
        
        Args:
            query: Search keywords
            language: Language code
            days_back: Number of days to search back
            limit: Number of news items to return
            
        Returns:
            News response or None
        """
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
            return news_response_from_dict(data)
        else:
            print("Note: News search request failed. Please check if API key is correct.")
            return None
    
    def get_category_news(self, category: str, 
                         language: str = "en",
                         limit: int = 10) -> Optional[NewsResponse]:
        """
        Get category news
        
        Args:
            category: News category
            language: Language code
            limit: Number of news items to return
            
        Returns:
            News response or None
        """
        if category not in NEWS_CATEGORIES:
            print(f"Invalid category: {category}. Available categories: {NEWS_CATEGORIES}")
            return None
        
        return self.get_top_headlines(language=language, category=category, limit=limit)
    
    def get_tech_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """Get technology news"""
        return self.get_category_news("technology", language, limit)
    
    def get_business_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """Get business news"""
        return self.get_category_news("business", language, limit)
    
    def get_sports_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """Get sports news"""
        return self.get_category_news("sports", language, limit)
    
    def get_health_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """Get health news"""
        return self.get_category_news("health", language, limit)
    
    def get_science_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """Get science news"""
        return self.get_category_news("science", language, limit)
    
    def get_entertainment_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """Get entertainment news"""
        return self.get_category_news("entertainment", language, limit)
    
    def get_general_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """Get general news"""
        return self.get_category_news("general", language, limit)
    
    def get_available_categories(self) -> List[str]:
        """Get available news categories"""
        return NEWS_CATEGORIES.copy()
    
    def get_available_locales(self) -> List[str]:
        """Get available locale codes"""
        return NEWS_LOCALES.copy()
    
    def get_available_languages(self) -> List[str]:
        """Get available language codes"""
        return NEWS_LANGUAGES.copy()
    
    def format_headlines(self, response: NewsResponse) -> str:
        """
        Format headlines
        
        Args:
            response: News response
            
        Returns:
            Formatted news string
        """
        if not response.data:
            return "No related news found"
        
        header = f"Top Headlines (Found {response.meta.found}, showing {response.meta.returned}):\n"
        return header + format_news_list(response.data)
    
    def format_search_results(self, response: NewsResponse, query: str) -> str:
        """
        Format search results
        
        Args:
            response: News response
            query: Search keywords
            
        Returns:
            Formatted search results string
        """
        if not response.data:
            return f"No news found related to '{query}'"
        
        header = f"Search results for '{query}' (Found {response.meta.found}, showing {response.meta.returned}):\n"
        return header + format_news_list(response.data)
    
    def format_category_news(self, response: NewsResponse, category: str) -> str:
        """
        Format category news
        
        Args:
            response: News response
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
    
    def comprehensive_news_search(self, query: str, 
                                 max_per_category: int = 3) -> str:
        """
        Comprehensive news search
        
        Args:
            query: Search keywords
            max_per_category: Maximum results per category
            
        Returns:
            Comprehensive search results string
        """
        results = []
        
        # Search related news
        search_results = self.search_news(query, limit=max_per_category * 2)
        if search_results and search_results.data:
            results.append(f"Search results for '{query}':")
            results.append(format_news_list(search_results.data[:max_per_category]))
        
        # Try to match categories
        query_lower = query.lower()
        category_matches = {
            "technology": ["tech", "technology", "ai", "software"],
            "business": ["business", "finance", "economy", "market"],
            "sports": ["sports", "game", "match", "tournament"],
            "health": ["health", "medical", "covid", "vaccine"],
            "science": ["science", "research", "study", "discovery"],
            "entertainment": ["entertainment", "movie", "celebrity", "film"]
        }
        
        for category, keywords in category_matches.items():
            if any(keyword in query_lower for keyword in keywords):
                category_results = self.get_category_news(category, limit=max_per_category)
                if category_results and category_results.data:
                    category_name = get_category_display_name(category)
                    results.append(f"\n{category_name} Related News:")
                    results.append(format_news_list(category_results.data))
                break
        
        return "\n\n".join(results) if results else f"No news found related to '{query}'" 