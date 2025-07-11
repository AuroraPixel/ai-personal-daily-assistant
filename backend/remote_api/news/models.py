"""
News API Data Models

Author: Andrew Wang
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class NewsSearchRequest(BaseModel):
    """News search request parameters"""
    query: Optional[str] = None
    locale: str = "us"
    language: str = "en"
    category: Optional[str] = None
    published_after: Optional[str] = None
    published_before: Optional[str] = None
    limit: int = 10


class NewsArticle(BaseModel):
    """News article information (single news item)"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    uuid: str                                   # Unique article identifier
    title: str                                  # Article headline title
    description: str                            # Article description/summary
    url: str                                    # Article URL link
    source: str                                 # News source name
    published_at: str                           # Publication timestamp (ISO8601)
    language: str                               # Article language code
    locale: Optional[str] = None                # Article locale/region code (optional)
    keywords: Optional[str] = None              # Article keywords (comma-separated)
    snippet: Optional[str] = None               # Article snippet/excerpt
    image_url: Optional[str] = None             # Article image URL
    categories: Optional[List[str]] = None      # Article categories list
    relevance_score: Optional[float] = None     # Search relevance score


class NewsMetadata(BaseModel):
    """News response metadata (pagination and result info)"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    found: int          # Total number of articles found
    returned: int       # Number of articles returned in this response
    limit: int          # Maximum number of articles requested
    page: int           # Current page number


class NewsApiResponse(BaseModel):
    """Universal news API response for all endpoints"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    meta: NewsMetadata              # Response metadata
    data: List[NewsArticle]         # List of news articles
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NewsApiResponse":
        """Create NewsApiResponse from dictionary using Pydantic's automatic mapping"""
        return cls(**data)


# Available news categories (as requested by user)
NEWS_CATEGORIES = [
    "general",
    "science", 
    "sports",
    "business",
    "health",
    "entertainment",
    "tech",
    "politics",
    "food",
    "travel"
]

# Available locale codes (as requested by user)
NEWS_LOCALES = [
    "ar",  # Argentina
    "am",  # Armenia
    "au",  # Australia
    "at",  # Austria
    "by",  # Belarus
    "be",  # Belgium
    "bo",  # Bolivia
    "br",  # Brazil
    "bg",  # Bulgaria
    "ca",  # Canada
    "cl",  # Chile
    "cn",  # China
    "co",  # Colombia
    "hr",  # Croatia
    "cz",  # Czechia
    "ec",  # Ecuador
    "eg",  # Egypt
    "fr",  # France
    "de",  # Germany
    "gr",  # Greece
    "hn",  # Honduras
    "hk",  # Hong Kong
    "in",  # India
    "id",  # Indonesia
    "ir",  # Iran
    "ie",  # Ireland
    "il",  # Israel
    "it",  # Italy
    "jp",  # Japan
    "kr",  # Korea
    "mx",  # Mexico
    "nl",  # Netherlands
    "nz",  # New Zealand
    "ni",  # Nicaragua
    "pk",  # Pakistan
    "pa",  # Panama
    "pe",  # Peru
    "pl",  # Poland
    "pt",  # Portugal
    "qa",  # Qatar
    "ro",  # Romania
    "ru",  # Russia
    "sa",  # Saudi Arabia
    "za",  # South Africa
    "es",  # Spain
    "ch",  # Switzerland
    "sy",  # Syria
    "tw",  # Taiwan
    "th",  # Thailand
    "tr",  # Turkey
    "ua",  # Ukraine
    "gb",  # United Kingdom
    "us",  # United States Of America
    "uy",  # Uruguay
    "ve"   # Venezuela
]

# Available language codes (ISO 639-1 standard)
NEWS_LANGUAGES = [
    "ar",       # Arabic
    "bg",       # Bulgarian  
    "bn",       # Bengali
    "cs",       # Czech
    "da",       # Danish
    "de",       # German
    "el",       # Greek
    "en",       # English
    "es",       # Spanish
    "et",       # Estonian
    "fa",       # Persian
    "fi",       # Finnish
    "fr",       # French
    "he",       # Hebrew
    "hi",       # Hindi
    "hr",       # Croatian
    "hu",       # Hungarian
    "id",       # Indonesian
    "it",       # Italian
    "ja",       # Japanese
    "ko",       # Korean
    "lt",       # Lithuanian
    "multi",    # Multiple languages
    "nl",       # Dutch
    "no",       # Norwegian
    "pl",       # Polish
    "pt",       # Portuguese
    "ro",       # Romanian
    "ru",       # Russian
    "sk",       # Slovak
    "sv",       # Swedish
    "ta",       # Tamil
    "th",       # Thai
    "tr",       # Turkish
    "uk",       # Ukrainian
    "vi",       # Vietnamese
    "zh"        # Chinese
]


def validate_category(category: str) -> bool:
    """Validate news category"""
    return category in NEWS_CATEGORIES


def validate_language(language: str) -> bool:
    """Validate language code"""
    return language in NEWS_LANGUAGES


def validate_locale(locale: str) -> bool:
    """Validate locale code"""
    return locale in NEWS_LOCALES


def get_category_error_message() -> str:
    """Get category validation error message"""
    return f"Invalid category. Available categories: {', '.join(NEWS_CATEGORIES)}"


def get_language_error_message() -> str:
    """Get language validation error message"""
    return f"Invalid language code. Available languages: {', '.join(NEWS_LANGUAGES)}"


def get_locale_error_message() -> str:
    """Get locale validation error message"""
    return f"Invalid locale code. Available locales: {', '.join(NEWS_LOCALES)}"


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
        "science": "Science",
        "sports": "Sports",
        "business": "Business",
        "health": "Health",
        "entertainment": "Entertainment",
        "tech": "Technology",
        "politics": "Politics",
        "food": "Food & Dining",
        "travel": "Travel"
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