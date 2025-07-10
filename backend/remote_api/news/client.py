"""
新闻API客户端
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
    """The News API新闻客户端"""
    
    def __init__(self):
        self.client = APIClient("https://api.thenewsapi.com/v1")
        # 从环境变量获取API token
        self.api_token = os.getenv("NEWS_API_TOKEN")
        if not self.api_token:
            print("警告：未找到环境变量 NEWS_API_TOKEN，新闻API可能无法正常工作")
    
    def _add_auth_params(self, params: dict) -> dict:
        """为请求参数添加认证信息"""
        if self.api_token:
            params["api_token"] = self.api_token
        return params
    
    def _debug_request(self, endpoint: str, params: dict):
        """调试输出请求信息"""
        print(f"调试：请求端点 {endpoint}")
        print(f"调试：请求参数 {params}")
        if not self.api_token:
            print("调试：未设置API token")
    
    def get_top_headlines(self, language: str = "en", 
                         category: Optional[str] = None,
                         limit: int = 10) -> Optional[NewsResponse]:
        """
        获取头条新闻
        
        Args:
            language: 语言代码
            category: 新闻分类
            limit: 返回新闻数量
            
        Returns:
            新闻响应或None
        """
        params = {
            "language": language,
            "limit": limit
        }
        
        if category:
            if category not in NEWS_CATEGORIES:
                print(f"无效分类: {category}. 可用分类: {NEWS_CATEGORIES}")
                return None
            params["categories"] = category
        
        # 添加认证参数
        params = self._add_auth_params(params)
        
        data = self.client.get("/news/all", params=params)
        
        if data:
            return news_response_from_dict(data)
        else:
            print("注意：新闻API请求失败。请检查API密钥是否正确。")
            return None
    
    def search_news(self, query: str, 
                   language: str = "en",
                   days_back: int = 7,
                   limit: int = 10) -> Optional[NewsResponse]:
        """
        搜索新闻
        
        Args:
            query: 搜索关键词
            language: 语言代码
            days_back: 搜索天数范围
            limit: 返回新闻数量
            
        Returns:
            新闻响应或None
        """
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
        
        # 添加认证参数
        params = self._add_auth_params(params)
        
        data = self.client.get("/news/all", params=params)
        
        if data:
            return news_response_from_dict(data)
        else:
            print("注意：新闻搜索请求失败。请检查API密钥是否正确。")
            return None
    
    def get_category_news(self, category: str, 
                         language: str = "en",
                         limit: int = 10) -> Optional[NewsResponse]:
        """
        获取分类新闻
        
        Args:
            category: 新闻分类
            language: 语言代码
            limit: 返回新闻数量
            
        Returns:
            新闻响应或None
        """
        if category not in NEWS_CATEGORIES:
            print(f"无效分类: {category}. 可用分类: {NEWS_CATEGORIES}")
            return None
        
        return self.get_top_headlines(language=language, category=category, limit=limit)
    
    def get_tech_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """获取科技新闻"""
        return self.get_category_news("technology", language, limit)
    
    def get_business_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """获取商业新闻"""
        return self.get_category_news("business", language, limit)
    
    def get_sports_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """获取体育新闻"""
        return self.get_category_news("sports", language, limit)
    
    def get_health_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """获取健康新闻"""
        return self.get_category_news("health", language, limit)
    
    def get_science_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """获取科学新闻"""
        return self.get_category_news("science", language, limit)
    
    def get_entertainment_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """获取娱乐新闻"""
        return self.get_category_news("entertainment", language, limit)
    
    def get_general_news(self, language: str = "en", limit: int = 10) -> Optional[NewsResponse]:
        """获取综合新闻"""
        return self.get_category_news("general", language, limit)
    
    def get_available_categories(self) -> List[str]:
        """获取可用的新闻分类"""
        return NEWS_CATEGORIES.copy()
    
    def get_available_locales(self) -> List[str]:
        """获取可用的地区代码"""
        return NEWS_LOCALES.copy()
    
    def get_available_languages(self) -> List[str]:
        """获取可用的语言代码"""
        return NEWS_LANGUAGES.copy()
    
    def format_headlines(self, response: NewsResponse) -> str:
        """
        格式化头条新闻
        
        Args:
            response: 新闻响应
            
        Returns:
            格式化的新闻字符串
        """
        if not response.data:
            return "没有找到相关新闻"
        
        header = f"头条新闻 (共找到 {response.meta.found} 条，显示 {response.meta.returned} 条):\n"
        return header + format_news_list(response.data)
    
    def format_search_results(self, response: NewsResponse, query: str) -> str:
        """
        格式化搜索结果
        
        Args:
            response: 新闻响应
            query: 搜索关键词
            
        Returns:
            格式化的搜索结果字符串
        """
        if not response.data:
            return f"没有找到与 '{query}' 相关的新闻"
        
        header = f"搜索 '{query}' 的结果 (共找到 {response.meta.found} 条，显示 {response.meta.returned} 条):\n"
        return header + format_news_list(response.data)
    
    def format_category_news(self, response: NewsResponse, category: str) -> str:
        """
        格式化分类新闻
        
        Args:
            response: 新闻响应
            category: 分类
            
        Returns:
            格式化的分类新闻字符串
        """
        if not response.data:
            return f"没有找到 {get_category_display_name(category)} 新闻"
        
        category_name = get_category_display_name(category)
        header = f"{category_name}新闻 (共找到 {response.meta.found} 条，显示 {response.meta.returned} 条):\n"
        return header + format_news_list(response.data)
    
    def get_article_details(self, article: NewsArticle) -> str:
        """
        获取文章详细信息
        
        Args:
            article: 新闻文章
            
        Returns:
            格式化的文章详细信息
        """
        return format_news_article(article)
    
    def comprehensive_news_search(self, query: str, 
                                 max_per_category: int = 3) -> str:
        """
        综合新闻搜索
        
        Args:
            query: 搜索关键词
            max_per_category: 每个分类的最大结果数
            
        Returns:
            综合搜索结果字符串
        """
        results = []
        
        # 搜索相关新闻
        search_results = self.search_news(query, limit=max_per_category * 2)
        if search_results and search_results.data:
            results.append(f"搜索结果 '{query}':")
            results.append(format_news_list(search_results.data[:max_per_category]))
        
        # 尝试匹配分类
        query_lower = query.lower()
        category_matches = {
            "technology": ["tech", "technology", "科技", "技术"],
            "business": ["business", "finance", "商业", "金融"],
            "sports": ["sports", "体育", "运动"],
            "health": ["health", "medical", "健康", "医疗"],
            "science": ["science", "research", "科学", "研究"],
            "entertainment": ["entertainment", "movie", "娱乐", "电影"]
        }
        
        for category, keywords in category_matches.items():
            if any(keyword in query_lower for keyword in keywords):
                category_results = self.get_category_news(category, limit=max_per_category)
                if category_results and category_results.data:
                    category_name = get_category_display_name(category)
                    results.append(f"\n{category_name}相关新闻:")
                    results.append(format_news_list(category_results.data))
                break
        
        return "\n\n".join(results) if results else f"没有找到与 '{query}' 相关的新闻" 