"""
AI 个人日常助手 - 主程序 (AI Personal Daily Assistant - Main Program)

启动 WebSocket 服务器和相关服务 (Start WebSocket server and related services)
"""

from datetime import datetime
import asyncio
from agents import Runner
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from remote_api.jsonplaceholder.client import JSONPlaceholderClient
from remote_api.news.client import NewsClient
import uvicorn

# 导入环境变量加载 (Import environment variable loading)
from dotenv import load_dotenv
load_dotenv()


from agent.personal_assistant import (
    coordination_agent,
    initialize_mcp_servers,
    cleanup_mcp_servers
)

async def main():
    print("🚀 正在启动AI个人日常助手...")
    
    # 1. 首先初始化MCP服务器
    print("📡 第1步: 初始化MCP服务器...")
    mcp_initialized = await initialize_mcp_servers()
    
    if not mcp_initialized:
        print("❌ MCP服务器初始化失败，程序退出")
        return
    
    print("✅ MCP服务器初始化成功")
    
    # 3. 确保MCP服务器初始化成功后，再执行Runner.run
    print("🤖 第3步: 开始运行智能代理...")
    
    success = False
    try:
        input = "给我推荐其中一个法餐，并给出它的详细做法，"
        result = await Runner.run(coordination_agent, input=input)
        print("✅ 代理运行成功")
        print(f"🎯 结果: {result.final_output}")
        success = True
    except Exception as e:
        print(f"❌ 代理运行失败: {e}")
    finally:
        # 4. 清理MCP服务器连接
        print("🧹 第4步: 清理MCP服务器连接...")
        await cleanup_mcp_servers()
    
    if success:
        print("🎉 程序执行完成")
    else:
        print("❌ 程序执行失败")

if __name__ == "__main__":
    asyncio.run(main())

