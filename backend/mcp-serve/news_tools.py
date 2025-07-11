"""
News Tools Module
Contains all news-related MCP tools

Author: Andrew Wang
"""

from fastmcp import FastMCP
from remote_api.news import NewsClient

# Initialize news client
news_client = NewsClient()  


def register_news_tools(mcp: FastMCP):
    """
    Register news tools to MCP instance
    
    Args:
        mcp: FastMCP instance
    """
    
    # Get top headlines
    @mcp.tool
    def get_top_headlines(language: str = "en", category: str = "", limit: int = 10) -> str:
        """
        Get top headlines
            Args:
                language: Language code (default English "en")
                category: News category (optional)
                limit: Number of news items to return (default 10)
            Returns:
                Top headlines list | Error message
        """
        try:
            category_param = category if category else None
            headlines = news_client.get_top_headlines(language, category_param, limit)
            if headlines:
                return news_client.format_headlines(headlines)
            return "Unable to get top headlines"
        except Exception as e:
            return f"Error getting top headlines: {str(e)}"

    # Search news
    @mcp.tool
    def search_news(query: str, language: str = "en", days_back: int = 7, limit: int = 10) -> str:
        """
        Search news
            Args:
                query: Search keywords
                language: Language code (default English "en")
                days_back: Number of days to search back (default 7 days)
                limit: Number of news items to return (default 10)
            Returns:
                Found news list | Error message
        """
        try:
            search_results = news_client.search_news(query, language, days_back, limit)
            if search_results:
                return news_client.format_search_results(search_results, query)
            return f"No news found about '{query}'"
        except Exception as e:
            return f"Error searching news: {str(e)}"

    # Get technology news
    @mcp.tool
    def get_tech_news(language: str = "en", limit: int = 10) -> str:
        """
        Get technology news
            Args:
                language: Language code (default English "en")
                limit: Number of news items to return (default 10)
            Returns:
                Technology news list | Error message
        """
        try:
            tech_news = news_client.get_tech_news(language, limit)
            if tech_news:
                return news_client.format_category_news(tech_news, "technology")
            return "Unable to get technology news"
        except Exception as e:
            return f"Error getting technology news: {str(e)}"

    # Get business news
    @mcp.tool
    def get_business_news(language: str = "en", limit: int = 10) -> str:
        """
        Get business news
            Args:
                language: Language code (default English "en")
                limit: Number of news items to return (default 10)
            Returns:
                Business news list | Error message
        """
        try:
            business_news = news_client.get_business_news(language, limit)
            if business_news:
                return news_client.format_category_news(business_news, "business")
            return "Unable to get business news"
        except Exception as e:
            return f"Error getting business news: {str(e)}"

    # Get sports news
    @mcp.tool
    def get_sports_news(language: str = "en", limit: int = 10) -> str:
        """
        Get sports news
            Args:
                language: Language code (default English "en")
                limit: Number of news items to return (default 10)
            Returns:
                Sports news list | Error message
        """
        try:
            sports_news = news_client.get_sports_news(language, limit)
            if sports_news:
                return news_client.format_category_news(sports_news, "sports")
            return "Unable to get sports news"
        except Exception as e:
            return f"Error getting sports news: {str(e)}"

    # Get health news
    @mcp.tool
    def get_health_news(language: str = "en", limit: int = 10) -> str:
        """
        Get health news
            Args:
                language: Language code (default English "en")
                limit: Number of news items to return (default 10)
            Returns:
                Health news list | Error message
        """
        try:
            health_news = news_client.get_health_news(language, limit)
            if health_news:
                return news_client.format_category_news(health_news, "health")
            return "Unable to get health news"
        except Exception as e:
            return f"Error getting health news: {str(e)}"

    # Get science news
    @mcp.tool
    def get_science_news(language: str = "en", limit: int = 10) -> str:
        """
        Get science news
            Args:
                language: Language code (default English "en")
                limit: Number of news items to return (default 10)
            Returns:
                Science news list | Error message
        """
        try:
            science_news = news_client.get_science_news(language, limit)
            if science_news:
                return news_client.format_category_news(science_news, "science")
            return "Unable to get science news"
        except Exception as e:
            return f"Error getting science news: {str(e)}"

    # Get entertainment news
    @mcp.tool
    def get_entertainment_news(language: str = "en", limit: int = 10) -> str:
        """
        Get entertainment news
            Args:
                language: Language code (default English "en")
                limit: Number of news items to return (default 10)
            Returns:
                Entertainment news list | Error message
        """
        try:
            entertainment_news = news_client.get_entertainment_news(language, limit)
            if entertainment_news:
                return news_client.format_category_news(entertainment_news, "entertainment")
            return "Unable to get entertainment news"
        except Exception as e:
            return f"Error getting entertainment news: {str(e)}"

    print("✅ News tools registered")