"""
News API Data Models

Author: Andrew Wang
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class NewsSearchRequest:
    """News search request parameters"""
    query: Optional[str] = None
    locale: str = "us"
    language: str = "en"
    category: Optional[str] = None
    published_after: Optional[str] = None
    published_before: Optional[str] = None
    limit: int = 10


@dataclass
class NewsArticle:
    """News article information"""
    uuid: str
    title: str
    description: str
    url: str
    source: str
    published_at: str
    language: str
    locale: str
    keywords: Optional[str] = None
    snippet: Optional[str] = None
    image_url: Optional[str] = None
    categories: Optional[List[str]] = None
    relevance_score: Optional[float] = None


@dataclass
class NewsMetadata:
    """News response metadata"""
    found: int
    returned: int
    limit: int
    page: int


@dataclass
class NewsResponse:
    """News API response"""
    meta: NewsMetadata
    data: List[NewsArticle]


# Available news categories
NEWS_CATEGORIES = [
    "general",
    "business",
    "entertainment",
    "health",
    "science",
    "sports",
    "technology"
]

# Available locales/regions
NEWS_LOCALES = [
    "us",  # United States
    "gb",  # United Kingdom
    "ca",  # Canada
    "au",  # Australia
    "in",  # India
    "jp",  # Japan
    "kr",  # South Korea
    "cn",  # China
    "de",  # Germany
    "fr",  # France
    "es",  # Spain
    "it",  # Italy
    "ru",  # Russia
    "br",  # Brazil
    "mx",  # Mexico
]

# Available languages
NEWS_LANGUAGES = [
    "en",  # English
    "zh",  # Chinese
    "ja",  # Japanese
    "ko",  # Korean
    "de",  # German
    "fr",  # French
    "es",  # Spanish
    "it",  # Italian
    "ru",  # Russian
    "pt",  # Portuguese
    "ar",  # Arabic
]


def news_article_from_dict(data: Dict) -> NewsArticle:
    """Create NewsArticle object from API response dictionary"""
    return NewsArticle(
        uuid=data["uuid"],
        title=data["title"],
        description=data["description"],
        url=data["url"],
        source=data["source"],
        published_at=data["published_at"],
        language=data.get("language", "en"),
        locale=data.get("locale", "us"),
        keywords=data.get("keywords"),
        snippet=data.get("snippet"),
        image_url=data.get("image_url"),
        categories=data.get("categories"),
        relevance_score=data.get("relevance_score")
    )


def news_metadata_from_dict(data: Dict) -> NewsMetadata:
    """Create NewsMetadata object from API response dictionary"""
    return NewsMetadata(
        found=data["found"],
        returned=data["returned"],
        limit=data["limit"],
        page=data["page"]
    )


def news_response_from_dict(data: Dict) -> NewsResponse:
    """Create NewsResponse object from API response dictionary"""
    meta = news_metadata_from_dict(data["meta"])
    articles = [news_article_from_dict(article_data) for article_data in data["data"]]
    
    return NewsResponse(meta=meta, data=articles)


def format_news_article(article: NewsArticle) -> str:
    """Format news article"""
    formatted = f"""
Title: {article.title}
Source: {article.source}
Published: {article.published_at}
Language: {article.language}
Locale: {article.locale}
    """.strip()
    
    if article.description:
        formatted += f"\nDescription: {article.description}"
    
    if article.keywords:
        formatted += f"\nKeywords: {article.keywords}"
    
    if article.categories:
        formatted += f"\nCategories: {', '.join(article.categories)}"
    
    formatted += f"\nURL: {article.url}"
    
    return formatted


def format_news_summary(article: NewsArticle) -> str:
    """Format news summary"""
    return f"{article.title} - {article.source} ({article.published_at})"


def format_news_list(articles: List[NewsArticle], max_items: int = 10) -> str:
    """Format news list"""
    if not articles:
        return "No related news found"
    
    formatted_articles = []
    for i, article in enumerate(articles[:max_items]):
        formatted_articles.append(f"{i+1}. {format_news_summary(article)}")
    
    result = "\n".join(formatted_articles)
    
    if len(articles) > max_items:
        result += f"\n... {len(articles) - max_items} more news items"
    
    return result


def get_category_display_name(category: str) -> str:
    """Get category display name in English"""
    category_names = {
        "general": "General",
        "business": "Business",
        "entertainment": "Entertainment",
        "health": "Health",
        "science": "Science",
        "sports": "Sports",
        "technology": "Technology"
    }
    return category_names.get(category, category)


def get_locale_display_name(locale: str) -> str:
    """Get locale display name in English"""
    locale_names = {
        "us": "United States",
        "gb": "United Kingdom",
        "ca": "Canada",
        "au": "Australia",
        "in": "India",
        "jp": "Japan",
        "kr": "South Korea",
        "cn": "China",
        "de": "Germany",
        "fr": "France",
        "es": "Spain",
        "it": "Italy",
        "ru": "Russia",
        "br": "Brazil",
        "mx": "Mexico"
    }
    return locale_names.get(locale, locale) 