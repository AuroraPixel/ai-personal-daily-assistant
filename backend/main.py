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
)

async def main():
 input = "今天天气怎么样？"
 result = await Runner.run(coordination_agent,input=input)
 print(result)

if __name__ == "__main__":
    asyncio.run(main())

