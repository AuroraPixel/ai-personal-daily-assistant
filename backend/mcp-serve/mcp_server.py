"""
AI Personal Daily Assistant MCP Service Main Entry
Unified loading and registration of all MCP tool modules

Author: Andrew Wang
"""

import sys
import os

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

def create_mcp_server():
    """
    Create and configure MCP server
    
    Returns:
        FastMCP: Configured MCP instance
    """
    print("🚀 Starting AI Personal Daily Assistant MCP Service...")
    
    # Create MCP instance
    mcp = FastMCP("MainApp")
    
    print("📦 Registering tool modules...")
    
    # Register all tool modules
    register_weather_tools(mcp)    # Register weather tools
    register_news_tools(mcp)       # Register news tools
    register_recipe_tools(mcp)     # Register recipe tools
    register_data_tools(mcp)       # Register data tools
    
    print("✅ All tool modules registered successfully!")
    print("🌟 MCP service is ready to handle requests")
    
    return mcp


def main():
    """
    Main function - Start MCP service
    """
    try:
        # Create MCP server
        mcp = create_mcp_server()
        
        # Start server
        print("🔌 Starting MCP server...")
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