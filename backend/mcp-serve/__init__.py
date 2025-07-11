"""
MCP Service Module Package
AI Personal Daily Assistant MCP Tools Service

Author: Andrew Wang
"""

__version__ = "1.0.0"
__author__ = "Andrew Wang"
__description__ = "MCP Tools Service Module"

# Export main modules
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