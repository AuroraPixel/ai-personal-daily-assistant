"""
AI个人日常助手MCP服务主入口 (AI Personal Daily Assistant MCP Service Main Entry)
统一加载和注册所有MCP工具模块
"""

from fastmcp import FastMCP
from weather_tools import register_weather_tools
from news_tools import register_news_tools
from recipe_tools import register_recipe_tools
from data_tools import register_data_tools

# =============================================================================
# MCP服务配置和初始化 (MCP Service Configuration and Initialization)
# =============================================================================

def create_mcp_server():
    """
    创建并配置MCP服务器
    Create and configure MCP server
    
    Returns:
        FastMCP: 配置好的MCP实例
    """
    print("🚀 正在启动AI个人日常助手MCP服务...")
    print("🚀 Starting AI Personal Daily Assistant MCP Service...")
    
    # 创建MCP实例 (Create MCP instance)
    mcp = FastMCP("AI Personal Daily Assistant MCP")
    
    print("📦 正在注册工具模块...")
    print("📦 Registering tool modules...")
    
    # 注册各个工具模块 (Register all tool modules)
    register_weather_tools(mcp)    # 注册天气工具
    register_news_tools(mcp)       # 注册新闻工具
    register_recipe_tools(mcp)     # 注册食谱工具
    register_data_tools(mcp)       # 注册数据工具
    
    print("✅ 所有工具模块注册完成！")
    print("✅ All tool modules registered successfully!")
    print("🌟 MCP服务已就绪，可以开始处理请求")
    print("🌟 MCP service is ready to handle requests")
    
    return mcp


def main():
    """
    主函数 - 启动MCP服务
    Main function - Start MCP service
    """
    try:
        # 创建MCP服务器
        mcp = create_mcp_server()
        
        # 启动服务器
        print("🔌 正在启动MCP服务器...")
        print("🔌 Starting MCP server...")
        mcp.run()
        
    except Exception as e:
        print(f"❌ 启动MCP服务时发生错误: {str(e)}")
        print(f"❌ Error starting MCP service: {str(e)}")
        raise


# =============================================================================
# 程序入口 (Program Entry Point)
# =============================================================================

if __name__ == "__main__":
    main()