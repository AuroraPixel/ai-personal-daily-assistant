"""
AI 个人日常助手 - 主应用入口

重构后的干净整洁的主应用文件，统一管理所有API模块
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入所有API路由器
from api import (
    auth_router,
    admin_router,
    conversation_router,
    websocket_router,
    system_router
)

# 导入WebSocket核心模块
from core.web_socket_core import connection_manager, WebSocketConfig

# 导入服务管理器
from service.service_manager import service_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# 初始化函数（从原文件移过来的）
# =========================
async def initialize_all_services():
    """初始化所有服务（优化版本）"""
    try:
        print("🚀 开始初始化所有服务...")
        
        # 1. 初始化服务管理器
        print("⚙️  正在初始化服务管理器...")
        if not service_manager.initialize():
            raise Exception("服务管理器初始化失败")
        print("✅ 服务管理器初始化完成")
        
        print("🎉 所有服务初始化完成")
            
    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        print("⚠️  应用将在有限功能下继续运行")

async def periodic_cache_cleanup():
    """定期清理过期缓存的后台任务"""
    while True:
        try:
            # 每30分钟清理一次过期缓存
            await asyncio.sleep(1800)  # 30分钟
            service_manager.clear_expired_cache()
            logger.info("定期清理过期缓存完成")
        except asyncio.CancelledError:
            logger.info("缓存清理任务已停止")
            break
        except Exception as e:
            logger.error(f"定期清理过期缓存失败: {e}")
            # 如果出错，等待10分钟后重试
            await asyncio.sleep(600)

# =========================
# 应用生命周期管理
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("启动 AI 个人日常助手服务...")
    
    # 初始化所有服务
    await initialize_all_services()
    
    # 启动心跳检测任务
    if not connection_manager.heartbeat_task:
        connection_manager.heartbeat_task = asyncio.create_task(
            connection_manager._heartbeat_loop()
        )
    
    # 启动定期缓存清理任务
    cache_cleanup_task = asyncio.create_task(periodic_cache_cleanup())
    
    logger.info("✅ AI 个人日常助手服务已启动")
    
    yield
    
    # 关闭时的清理
    logger.info("关闭 AI 个人日常助手服务...")
    
    # 停止心跳检测任务
    if connection_manager.heartbeat_task:
        connection_manager.heartbeat_task.cancel()
        try:
            await connection_manager.heartbeat_task
        except asyncio.CancelledError:
            pass
    
    # 停止缓存清理任务
    cache_cleanup_task.cancel()
    try:
        await cache_cleanup_task
    except asyncio.CancelledError:
        pass
    
    # 关闭服务管理器（统一关闭所有服务）
    try:
        service_manager.close()
        logger.info("✅ 服务管理器已关闭")
    except Exception as service_cleanup_error:
        logger.error(f"⚠️  关闭服务管理器时发生错误: {service_cleanup_error}")
    
    logger.info("✅ AI 个人日常助手服务已关闭")

# =========================
# 创建 FastAPI 应用
# =========================
app = FastAPI(
    title="AI 个人日常助手服务",
    description="提供认证、会话管理、WebSocket通信等功能的智能助手服务",
    version="1.0.0",
    lifespan=lifespan
)

# =========================
# 添加中间件
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 注册所有路由器
# =========================

# 系统路由器（根路径）
app.include_router(system_router)

# 认证路由器
app.include_router(auth_router)

# 管理员路由器
app.include_router(admin_router)

# 会话路由器
app.include_router(conversation_router)

# WebSocket路由器（包含所有WebSocket相关端点）
app.include_router(websocket_router)

# =========================
# 主程序入口
# =========================
if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=WebSocketConfig.DEFAULT_PORT,
        log_level="info",
        reload=True
    ) 