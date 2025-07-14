"""
管理员API模块

包含缓存管理等管理员功能的API端点
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter

# 导入认证核心模块
from core.auth_core import CurrentUser

# 导入服务管理器
from service.service_manager import service_manager

# 配置日志
logger = logging.getLogger(__name__)

# 创建管理员API路由器
admin_router = APIRouter(prefix="/admin", tags=["管理员"])

# =========================
# API端点
# =========================

@admin_router.post("/cache/clear")
async def clear_cache(current_user: Dict[str, Any] = CurrentUser):
    """清理所有缓存（管理员功能）"""
    try:
        # 清理服务管理器缓存
        service_manager.clear_cache()
        
        # 获取清理后的统计信息
        stats = service_manager.get_stats()
        
        return {
            "success": True,
            "message": "缓存已清理",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"清理缓存失败: {e}")
        return {
            "success": False,
            "message": f"清理缓存失败: {str(e)}"
        }


@admin_router.post("/cache/cleanup")
async def cleanup_expired_cache(current_user: Dict[str, Any] = CurrentUser):
    """清理过期缓存（管理员功能）"""
    try:
        # 清理过期缓存
        service_manager.clear_expired_cache()
        
        # 获取清理后的统计信息
        stats = service_manager.get_stats()
        
        return {
            "success": True,
            "message": "过期缓存已清理",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"清理过期缓存失败: {e}")
        return {
            "success": False,
            "message": f"清理过期缓存失败: {str(e)}"
        } 