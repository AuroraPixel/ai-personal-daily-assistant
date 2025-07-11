"""
AI 个人日常助手 - 主程序 (AI Personal Daily Assistant - Main Program)

启动 WebSocket 服务器和相关服务 (Start WebSocket server and related services)
"""

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from remote_api.jsonplaceholder.client import JSONPlaceholderClient
from remote_api.news.client import NewsClient
import uvicorn

# 导入环境变量加载 (Import environment variable loading)
from dotenv import load_dotenv
load_dotenv()
news_client = NewsClient()



news_response = news_client.get_news(language="zh", category="general", limit=10)

print(news_response)
