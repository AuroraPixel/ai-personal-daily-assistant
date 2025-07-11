"""
新闻工具模块 (News Tools Module)
包含所有新闻相关的MCP工具
"""

from fastmcp import FastMCP
from remote_api.news import NewsClient

# 初始化新闻客户端 (Initialize news client)
news_client = NewsClient()  


def register_news_tools(mcp: FastMCP):
    """
    注册新闻工具到MCP实例
    Register news tools to MCP instance
    
    Args:
        mcp: FastMCP实例
    """
    
    # 获取头条新闻 (Get top headlines)
    @mcp.tool
    def get_top_headlines(language: str = "en", category: str = "", limit: int = 10) -> str:
        """
        获取头条新闻
            Args:
                language: 语言代码 (默认英语 "en")
                category: 新闻分类 (可选)
                limit: 返回新闻数量 (默认10条)
            Returns:
                头条新闻列表 | 错误信息
        """
        try:
            category_param = category if category else None
            headlines = news_client.get_top_headlines(language, category_param, limit)
            if headlines:
                return news_client.format_headlines(headlines)
            return "无法获取头条新闻"
        except Exception as e:
            return f"获取头条新闻时出错: {str(e)}"

    # 搜索新闻 (Search news)
    @mcp.tool
    def search_news(query: str, language: str = "en", days_back: int = 7, limit: int = 10) -> str:
        """
        搜索新闻
            Args:
                query: 搜索关键词
                language: 语言代码 (默认英语 "en")
                days_back: 搜索天数范围 (默认7天)
                limit: 返回新闻数量 (默认10条)
            Returns:
                搜索到的新闻列表 | 错误信息
        """
        try:
            search_results = news_client.search_news(query, language, days_back, limit)
            if search_results:
                return news_client.format_search_results(search_results, query)
            return f"未找到关于'{query}'的新闻"
        except Exception as e:
            return f"搜索新闻时出错: {str(e)}"

    # 获取科技新闻 (Get technology news)
    @mcp.tool
    def get_tech_news(language: str = "en", limit: int = 10) -> str:
        """
        获取科技新闻
            Args:
                language: 语言代码 (默认英语 "en")
                limit: 返回新闻数量 (默认10条)
            Returns:
                科技新闻列表 | 错误信息
        """
        try:
            tech_news = news_client.get_tech_news(language, limit)
            if tech_news:
                return news_client.format_category_news(tech_news, "technology")
            return "无法获取科技新闻"
        except Exception as e:
            return f"获取科技新闻时出错: {str(e)}"

    # 获取商业新闻 (Get business news)
    @mcp.tool
    def get_business_news(language: str = "en", limit: int = 10) -> str:
        """
        获取商业新闻
            Args:
                language: 语言代码 (默认英语 "en")
                limit: 返回新闻数量 (默认10条)
            Returns:
                商业新闻列表 | 错误信息
        """
        try:
            business_news = news_client.get_business_news(language, limit)
            if business_news:
                return news_client.format_category_news(business_news, "business")
            return "无法获取商业新闻"
        except Exception as e:
            return f"获取商业新闻时出错: {str(e)}"

    # 获取体育新闻 (Get sports news)
    @mcp.tool
    def get_sports_news(language: str = "en", limit: int = 10) -> str:
        """
        获取体育新闻
            Args:
                language: 语言代码 (默认英语 "en")
                limit: 返回新闻数量 (默认10条)
            Returns:
                体育新闻列表 | 错误信息
        """
        try:
            sports_news = news_client.get_sports_news(language, limit)
            if sports_news:
                return news_client.format_category_news(sports_news, "sports")
            return "无法获取体育新闻"
        except Exception as e:
            return f"获取体育新闻时出错: {str(e)}"

    # 获取健康新闻 (Get health news)
    @mcp.tool
    def get_health_news(language: str = "en", limit: int = 10) -> str:
        """
        获取健康新闻
            Args:
                language: 语言代码 (默认英语 "en")
                limit: 返回新闻数量 (默认10条)
            Returns:
                健康新闻列表 | 错误信息
        """
        try:
            health_news = news_client.get_health_news(language, limit)
            if health_news:
                return news_client.format_category_news(health_news, "health")
            return "无法获取健康新闻"
        except Exception as e:
            return f"获取健康新闻时出错: {str(e)}"

    # 获取科学新闻 (Get science news)
    @mcp.tool
    def get_science_news(language: str = "en", limit: int = 10) -> str:
        """
        获取科学新闻
            Args:
                language: 语言代码 (默认英语 "en")
                limit: 返回新闻数量 (默认10条)
            Returns:
                科学新闻列表 | 错误信息
        """
        try:
            science_news = news_client.get_science_news(language, limit)
            if science_news:
                return news_client.format_category_news(science_news, "science")
            return "无法获取科学新闻"
        except Exception as e:
            return f"获取科学新闻时出错: {str(e)}"

    # 获取娱乐新闻 (Get entertainment news)
    @mcp.tool
    def get_entertainment_news(language: str = "en", limit: int = 10) -> str:
        """
        获取娱乐新闻
            Args:
                language: 语言代码 (默认英语 "en")
                limit: 返回新闻数量 (默认10条)
            Returns:
                娱乐新闻列表 | 错误信息
        """
        try:
            entertainment_news = news_client.get_entertainment_news(language, limit)
            if entertainment_news:
                return news_client.format_category_news(entertainment_news, "entertainment")
            return "无法获取娱乐新闻"
        except Exception as e:
            return f"获取娱乐新闻时出错: {str(e)}"

    print("✅ 新闻工具已注册 (News tools registered)")