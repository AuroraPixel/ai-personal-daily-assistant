#!/usr/bin/env python3
"""
启动 AI 个人日常助手 WebSocket 流式服务
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# 确保 backend 目录在 Python 路径中
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """启动 WebSocket 服务"""
    print("🚀 启动 AI 个人日常助手 WebSocket 流式服务...")
    print("📍 测试页面: http://localhost:8000/test")
    print("🔗 WebSocket 端点: ws://localhost:8000/ws")
    print("📝 使用说明:")
    print("   1. 访问 http://localhost:8000/test 进行测试")
    print("   2. 输入用户ID (必需)")
    print("   3. 连接后发送聊天消息")
    print("   4. 观察 AI 流式响应")
    print("-" * 50)
    
    try:
        # 启动 uvicorn 服务器
        uvicorn.run(
            "main_socket_agent:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 