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
from user_data_tools import register_user_data_tools

# Import database initialization components
from core.database_core import DatabaseClient
from core.vector_core import ChromaVectorClient, VectorConfig

# =============================================================================
# MCP Service Configuration and Initialization
# =============================================================================

weather_mcp = FastMCP("Weather")
register_weather_tools(weather_mcp)    # Register weather tools
news_mcp = FastMCP("News")
register_news_tools(news_mcp)       # Register news tools
recipe_mcp = FastMCP("Recipe")
register_recipe_tools(recipe_mcp)     # Register recipe tools
user_data_mcp = FastMCP("UserData")
register_user_data_tools(user_data_mcp)  # Register user data tools

mcp = FastMCP("MainApp")

def initialize_databases():
    """
    Initialize MySQL and Vector databases
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        print("🔄 Initializing databases...")
        
        # Initialize MySQL database
        print("📊 Initializing MySQL database...")
        db_client = DatabaseClient()
        if not db_client.initialize():
            print("❌ MySQL database initialization failed")
            return False
        
        # Create tables if they don't exist
        if not db_client.create_tables():
            print("❌ Failed to create database tables")
            return False
        
        print("✅ MySQL database initialized successfully")
        
        # Initialize vector database
        print("🔍 Initializing vector database...")
        try:
            vector_config = VectorConfig.from_env()
            vector_client = ChromaVectorClient(vector_config)
            health = vector_client.health_check()
            if health.get('status') != 'healthy':
                print("⚠️  Vector database health check failed")
            else:
                print("✅ Vector database initialized successfully")
        except Exception as e:
            print(f"⚠️  Vector database initialization failed: {e}")
            print("    MCP service will continue without vector search capabilities")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

async def create_mcp_server():
    """
    Create and configure MCP server
    
    Returns:
        FastMCP: Configured MCP instance
    """
    print("🚀 Starting AI Personal Daily Assistant MCP Service...")
    
    # Initialize databases first
    if not initialize_databases():
        print("❌ Database initialization failed, but continuing with MCP service")
    
    # Create MCP instance
    await mcp.import_server(weather_mcp, prefix="weather")
    await mcp.import_server(news_mcp, prefix="news")
    await mcp.import_server(recipe_mcp, prefix="recipe")
    await mcp.import_server(user_data_mcp, prefix="user_data")
    
    print("📦 Registering tool modules...")
    
    # Register all tool modules
    # All tools are registered during import_server calls
    
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