"""
新闻API数据模型
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class NewsSearchRequest:
    """新闻搜索请求参数"""
    query: Optional[str] = None
    locale: str = "us"
    language: str = "en"
    category: Optional[str] = None
    published_after: Optional[str] = None
    published_before: Optional[str] = None
    limit: int = 10


@dataclass
class NewsArticle:
    """新闻文章信息"""
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
    """新闻响应元数据"""
    found: int
    returned: int
    limit: int
    page: int


@dataclass
class NewsResponse:
    """新闻API响应"""
    meta: NewsMetadata
    data: List[NewsArticle]


# 可用的新闻分类
NEWS_CATEGORIES = [
    "general",
    "business",
    "entertainment",
    "health",
    "science",
    "sports",
    "technology"
]

# 可用的地区/语言
NEWS_LOCALES = [
    "us",  # 美国
    "gb",  # 英国
    "ca",  # 加拿大
    "au",  # 澳大利亚
    "in",  # 印度
    "jp",  # 日本
    "kr",  # 韩国
    "cn",  # 中国
    "de",  # 德国
    "fr",  # 法国
    "es",  # 西班牙
    "it",  # 意大利
    "ru",  # 俄罗斯
    "br",  # 巴西
    "mx",  # 墨西哥
]

# 可用的语言
NEWS_LANGUAGES = [
    "en",  # 英语
    "zh",  # 中文
    "ja",  # 日语
    "ko",  # 韩语
    "de",  # 德语
    "fr",  # 法语
    "es",  # 西班牙语
    "it",  # 意大利语
    "ru",  # 俄语
    "pt",  # 葡萄牙语
    "ar",  # 阿拉伯语
]


def news_article_from_dict(data: Dict) -> NewsArticle:
    """从API响应字典创建NewsArticle对象"""
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
    """从API响应字典创建NewsMetadata对象"""
    return NewsMetadata(
        found=data["found"],
        returned=data["returned"],
        limit=data["limit"],
        page=data["page"]
    )


def news_response_from_dict(data: Dict) -> NewsResponse:
    """从API响应字典创建NewsResponse对象"""
    meta = news_metadata_from_dict(data["meta"])
    articles = [news_article_from_dict(article_data) for article_data in data["data"]]
    
    return NewsResponse(meta=meta, data=articles)


def format_news_article(article: NewsArticle) -> str:
    """格式化新闻文章"""
    formatted = f"""
标题: {article.title}
来源: {article.source}
发布时间: {article.published_at}
语言: {article.language}
地区: {article.locale}
    """.strip()
    
    if article.description:
        formatted += f"\n摘要: {article.description}"
    
    if article.keywords:
        formatted += f"\n关键词: {article.keywords}"
    
    if article.categories:
        formatted += f"\n分类: {', '.join(article.categories)}"
    
    formatted += f"\n链接: {article.url}"
    
    return formatted


def format_news_summary(article: NewsArticle) -> str:
    """格式化新闻摘要"""
    return f"{article.title} - {article.source} ({article.published_at})"


def format_news_list(articles: List[NewsArticle], max_items: int = 10) -> str:
    """格式化新闻列表"""
    if not articles:
        return "没有找到相关新闻"
    
    formatted_articles = []
    for i, article in enumerate(articles[:max_items]):
        formatted_articles.append(f"{i+1}. {format_news_summary(article)}")
    
    result = "\n".join(formatted_articles)
    
    if len(articles) > max_items:
        result += f"\n... 还有 {len(articles) - max_items} 条新闻"
    
    return result


def get_category_display_name(category: str) -> str:
    """获取分类的中文显示名称"""
    category_names = {
        "general": "综合",
        "business": "商业",
        "entertainment": "娱乐",
        "health": "健康",
        "science": "科学",
        "sports": "体育",
        "technology": "科技"
    }
    return category_names.get(category, category)


def get_locale_display_name(locale: str) -> str:
    """获取地区的中文显示名称"""
    locale_names = {
        "us": "美国",
        "gb": "英国",
        "ca": "加拿大",
        "au": "澳大利亚",
        "in": "印度",
        "jp": "日本",
        "kr": "韩国",
        "cn": "中国",
        "de": "德国",
        "fr": "法国",
        "es": "西班牙",
        "it": "意大利",
        "ru": "俄罗斯",
        "br": "巴西",
        "mx": "墨西哥"
    }
    return locale_names.get(locale, locale) 