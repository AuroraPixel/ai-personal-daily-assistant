"""
MCP服务模块包 (MCP Service Module Package)
AI个人日常助手MCP工具服务
"""

__version__ = "1.0.0"
__author__ = "AI Personal Daily Assistant"
__description__ = "MCP工具服务模块 (MCP Tools Service Module)"

# 导出主要模块
from .mcp_server import create_mcp_server, main
from .weather_tools import register_weather_tools
from .news_tools import register_news_tools
from .recipe_tools import register_recipe_tools
from .data_tools import register_data_tools

__all__ = [
    "create_mcp_server",
    "main",
    "register_weather_tools",
    "register_news_tools", 
    "register_recipe_tools",
    "register_data_tools"
]