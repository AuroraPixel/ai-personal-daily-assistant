"""
会话API模块

包含用户会话列表、聊天记录等会话相关的API端点
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel

# 导入认证核心模块
from core.auth_core import CurrentUser

# 导入服务管理器
from service.service_manager import service_manager

# 导入服务类
from service.services.conversation_service import ConversationService
from service.services.chat_message_service import ChatMessageService

# 配置日志
logger = logging.getLogger(__name__)

# 创建会话API路由器
conversation_router = APIRouter(prefix="/api/conversations", tags=["会话"])

# =========================
# 数据模型
# =========================

class ConversationListResponse(BaseModel):
    """会话列表响应模型"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    total: int = 0
    user_id: int


class ChatMessageResponse(BaseModel):
    """聊天记录响应模型"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    total: int = 0
    conversation_id: str
    conversation_info: Optional[Dict[str, Any]] = None

# =========================
# API端点
# =========================

@conversation_router.get("/{user_id}")
async def get_user_conversations(
    user_id: int = Path(..., description="用户ID"),
    status: Optional[str] = Query(None, description="会话状态过滤（active/inactive/archived）"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取用户的会话列表
    
    Args:
        user_id: 用户ID
        status: 会话状态过滤（可选）
        limit: 返回数量限制
        offset: 偏移量
        current_user: 当前认证用户
        
    Returns:
        会话列表响应
    """
    try:
        # 验证用户只能访问自己的会话 - 这是第一优先级检查
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问其他用户的会话")
        
        # 使用服务管理器获取会话服务
        conversation_service = service_manager.get_service(
            'conversation_service',
            ConversationService
        )
        
        # 获取用户会话列表
        conversations = conversation_service.get_user_conversations(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        # 转换为响应格式
        conversations_data = []
        for conv in conversations:
            conversation_data = {
                "id": conv.id,
                "id_str": conv.id_str,
                "user_id": conv.user_id,
                "title": conv.title,
                "description": conv.description,
                "status": conv.status,
                "last_active": conv.last_active.isoformat() if conv.last_active is not None else None,
                "created_at": conv.created_at.isoformat() if conv.created_at is not None else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at is not None else None
            }
            conversations_data.append(conversation_data)
        
        # 获取总数统计
        total_conversations = len(conversations)
        
        # 不需要关闭服务，使用共享实例
        
        return ConversationListResponse(
            success=True,
            message=f"成功获取用户 {user_id} 的会话列表",
            data=conversations_data,
            total=total_conversations,
            user_id=user_id
        )
        
    except HTTPException:
        # 重新抛出HTTP异常（如403权限错误）
        raise
    except Exception as e:
        logger.error(f"获取用户会话列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")


@conversation_router.get("/{conversation_id_str}/messages")
async def get_conversation_messages(
    conversation_id_str: str = Path(..., description="会话ID字符串"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    order_desc: bool = Query(True, description="是否按创建时间倒序排列"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取会话的聊天记录
    
    Args:
        conversation_id_str: 会话ID字符串
        limit: 返回数量限制
        offset: 偏移量
        order_desc: 是否按创建时间倒序排列
        current_user: 当前认证用户
        
    Returns:
        聊天记录响应
    """
    try:
        # 使用服务管理器获取服务
        conversation_service = service_manager.get_service(
            'conversation_service',
            ConversationService
        )
        chat_message_service = service_manager.get_service(
            'chat_message_service',
            ChatMessageService
        )
        
        # 验证会话是否存在
        conversation = conversation_service.get_conversation_by_id_str(conversation_id_str)
        if not conversation:
            raise HTTPException(status_code=404, detail=f"会话 {conversation_id_str} 不存在")
        
        # 验证用户只能访问自己的会话
        if str(conversation.user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问其他用户的会话消息")
        
        # 获取聊天记录
        messages = chat_message_service.get_conversation_messages_by_id_str(
            conversation_id_str=conversation_id_str,
            limit=limit,
            offset=offset,
            order_desc=order_desc
        )
        
        # 转换为响应格式
        messages_data = []
        for msg in messages:
            message_data = {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "conversation_id_str": msg.conversation_id_str,
                "sender_type": msg.sender_type,
                "sender_id": msg.sender_id,
                "content": msg.content,
                "message_type": msg.message_type,
                "status": msg.status,
                "reply_to_id": msg.reply_to_id,
                "extra_data": msg.extra_data,
                "created_at": msg.created_at.isoformat() if msg.created_at is not None else None,
                "updated_at": msg.updated_at.isoformat() if msg.updated_at is not None else None
            }
            messages_data.append(message_data)
        
        # 获取会话信息
        conversation_info = {
            "id": conversation.id,
            "id_str": conversation.id_str,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "description": conversation.description,
            "status": conversation.status,
            "last_active": conversation.last_active.isoformat() if conversation.last_active is not None else None,
            "created_at": conversation.created_at.isoformat() if conversation.created_at is not None else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at is not None else None
        }
        
        # 获取总消息数
        total_messages = len(messages)
        
        # 不需要关闭服务，使用共享实例
        
        return ChatMessageResponse(
            success=True,
            message=f"成功获取会话 {conversation_id_str} 的聊天记录",
            data=messages_data,
            total=total_messages,
            conversation_id=conversation_id_str,
            conversation_info=conversation_info
        )
        
    except HTTPException:
        # 重新抛出HTTP异常（如403权限错误、404不存在等）
        raise
    except Exception as e:
        logger.error(f"获取会话聊天记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取聊天记录失败: {str(e)}") 