"""
AI Personal Daily Assistant MCP Service Main Entry
Unified loading and registration of all MCP tool modules

Author: Andrew Wang
"""

import sys
import os
import asyncio

# Add backend directory to Python path so we can import remote_api modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from fastmcp import FastMCP
from weather_tools import register_weather_tools
from news_tools import register_news_tools
from recipe_tools import register_recipe_tools
from data_tools import register_data_tools

# =============================================================================
# MCP Service Configuration and Initialization
# =============================================================================

weather_mcp = FastMCP("Weather")
register_weather_tools(weather_mcp)    # Register weather tools
news_mcp = FastMCP("News")
register_news_tools(news_mcp)       # Register news tools
recipe_mcp = FastMCP("Recipe")
register_recipe_tools(recipe_mcp)     # Register recipe tools
data_mcp = FastMCP("Data")
register_data_tools(data_mcp)

mcp = FastMCP("MainApp")

async def create_mcp_server():
    """
    Create and configure MCP server
    
    Returns:
        FastMCP: Configured MCP instance
    """
    print("🚀 Starting AI Personal Daily Assistant MCP Service...")
    
    # Create MCP instance
    await mcp.import_server(weather_mcp, prefix="weather")
    await mcp.import_server(news_mcp, prefix="news")
    await mcp.import_server(recipe_mcp, prefix="recipe")
    await mcp.import_server(data_mcp, prefix="data")
    
    print("📦 Registering tool modules...")
    
    # Register all tool modules
    # Register data tools
    
    print("✅ All tool modules registered successfully!")
    print("🌟 MCP service is ready to handle requests")
    
    return mcp


def main():
    """
    Main function - Start MCP service
    """
    try:    
        # Start server
        print("🔌 Starting MCP server...")
        asyncio.run(create_mcp_server())
        mcp.run(
            transport="http",
            host="127.0.0.1", 
            port=8002,
            path="/mcp"
        )
        
    except Exception as e:
        print(f"❌ Error starting MCP service: {str(e)}")
        raise


# =============================================================================
# Program Entry Point
# =============================================================================

if __name__ == "__main__":
    main()