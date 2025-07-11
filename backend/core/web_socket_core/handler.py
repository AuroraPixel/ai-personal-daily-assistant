"""
WebSocket 消息处理器 (WebSocket Message Handler)
处理不同类型的 WebSocket 消息，包括系统消息、用户消息、AI 消息等
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .models import (
    WebSocketMessage, 
    MessageType, 
    UserInfo, 
    ConnectionInfo,
    RoomInfo,
    WebSocketError
)
from .manager import WebSocketConnectionManager

# 配置日志 (Configure logging)
logger = logging.getLogger(__name__)


class WebSocketMessageHandler:
    """
    WebSocket 消息处理器 (WebSocket Message Handler)
    
    负责处理各种类型的 WebSocket 消息 (Handles various types of WebSocket messages):
    - 系统消息 (System messages): CONNECT, DISCONNECT, PING, PONG, ERROR
    - 用户消息 (User messages): CHAT, NOTIFICATION, COMMAND, DATA
    - AI 消息 (AI messages): AI_RESPONSE, AI_THINKING, AI_ERROR
    """
    
    def __init__(self, connection_manager: WebSocketConnectionManager):
        """
        初始化消息处理器 (Initialize message handler)
        
        Args:
            connection_manager: WebSocket 连接管理器 (WebSocket connection manager)
        """
        self.connection_manager = connection_manager
        self.command_handlers: Dict[str, callable] = {}
        
        # 注册默认消息处理器 (Register default message handlers)
        self._register_default_handlers()
        
        logger.info("WebSocket 消息处理器已初始化 (WebSocket Message Handler initialized)")

    def _register_default_handlers(self):
        """注册默认的消息处理器 (Register default message handlers)"""
        # 系统消息处理器 (System message handlers)
        self.connection_manager.register_message_handler(MessageType.PING, self.handle_ping)
        self.connection_manager.register_message_handler(MessageType.PONG, self.handle_pong)
        self.connection_manager.register_message_handler(MessageType.CONNECT, self.handle_connect)
        self.connection_manager.register_message_handler(MessageType.DISCONNECT, self.handle_disconnect)
        
        # 用户消息处理器 (User message handlers)
        self.connection_manager.register_message_handler(MessageType.CHAT, self.handle_chat)
        self.connection_manager.register_message_handler(MessageType.NOTIFICATION, self.handle_notification)
        self.connection_manager.register_message_handler(MessageType.COMMAND, self.handle_command)
        self.connection_manager.register_message_handler(MessageType.DATA, self.handle_data)
        
        # AI 消息处理器 (AI message handlers)
        self.connection_manager.register_message_handler(MessageType.AI_RESPONSE, self.handle_ai_response)
        self.connection_manager.register_message_handler(MessageType.AI_THINKING, self.handle_ai_thinking)
        self.connection_manager.register_message_handler(MessageType.AI_ERROR, self.handle_ai_error)

    async def handle_ping(self, connection_id: str, message: WebSocketMessage):
        """
        处理心跳检测消息 (Handle ping message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 心跳消息 (Ping message)
        """
        # 发送 PONG 响应 (Send PONG response)
        pong_message = WebSocketMessage(
            type=MessageType.PONG,
            content={"timestamp": datetime.utcnow().isoformat()},
            sender_id=None,
            receiver_id=None,
            room_id=None,
            timestamp=datetime.utcnow()
        )
        
        await self.connection_manager.send_to_connection(connection_id, pong_message)
        logger.debug(f"发送 PONG 响应 (Sent PONG response): {connection_id}")

    async def handle_pong(self, connection_id: str, message: WebSocketMessage):
        """
        处理心跳响应消息 (Handle pong message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 心跳响应消息 (Pong message)
        """
        # 更新连接的最后心跳时间 (Update connection's last ping time)
        await self.connection_manager.handle_pong(connection_id)
        logger.debug(f"接收到 PONG 响应 (Received PONG response): {connection_id}")

    async def handle_connect(self, connection_id: str, message: WebSocketMessage):
        """
        处理连接消息 (Handle connect message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 连接消息 (Connect message)
        """
        logger.info(f"处理连接消息 (Handling connect message): {connection_id}")
        
        # 发送欢迎消息 (Send welcome message)
        welcome_message = WebSocketMessage(
            type=MessageType.NOTIFICATION,
            content={
                "type": "welcome",
                "message": "欢迎连接到 AI 个人日常助手！(Welcome to AI Personal Daily Assistant!)",
                "timestamp": datetime.utcnow().isoformat()
            },
            sender_id="system",
            receiver_id=None,
            room_id=None,
            timestamp=datetime.utcnow()
        )
        
        await self.connection_manager.send_to_connection(connection_id, welcome_message)

    async def handle_disconnect(self, connection_id: str, message: WebSocketMessage):
        """
        处理断开连接消息 (Handle disconnect message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 断开连接消息 (Disconnect message)
        """
        logger.info(f"处理断开连接消息 (Handling disconnect message): {connection_id}")
        
        # 获取连接信息 (Get connection info)
        conn_info = await self.connection_manager.get_connection_info(connection_id)
        if conn_info and conn_info.user_info:
            # 通知其他用户此用户已离线 (Notify other users that this user is offline)
            offline_message = WebSocketMessage(
                type=MessageType.NOTIFICATION,
                content={
                    "type": "user_offline",
                    "user_id": conn_info.user_info.user_id,
                    "username": conn_info.user_info.username,
                    "timestamp": datetime.utcnow().isoformat()
                },
                sender_id="system",
                receiver_id=None,
                room_id=None,
                timestamp=datetime.utcnow()
            )
            
            await self.connection_manager.broadcast_to_all(
                offline_message, 
                exclude_connections=[connection_id]
            )

    async def handle_chat(self, connection_id: str, message: WebSocketMessage):
        """
        处理聊天消息 (Handle chat message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 聊天消息 (Chat message)
        """
        logger.info(f"处理聊天消息 (Handling chat message): {connection_id}")
        
        # 获取发送者信息 (Get sender info)
        conn_info = await self.connection_manager.get_connection_info(connection_id)
        if not conn_info or not conn_info.user_info:
            # 发送错误消息 (Send error message)
            error_message = WebSocketMessage(
                type=MessageType.ERROR,
                content={"error": "未认证用户无法发送聊天消息 (Unauthenticated user cannot send chat messages)"},
                sender_id="system",
                receiver_id=None,
                room_id=None,
                timestamp=datetime.utcnow()
            )
            await self.connection_manager.send_to_connection(connection_id, error_message)
            return

        # 设置发送者信息 (Set sender info)
        message.sender_id = conn_info.user_info.user_id
        
        # 根据目标类型分发消息 (Distribute message based on target type)
        if message.receiver_id:
            # 私聊消息 (Private message)
            await self.connection_manager.send_to_user(message.receiver_id, message)
        elif message.room_id:
            # 房间消息 (Room message)
            await self.connection_manager.broadcast_to_room(message.room_id, message)
        else:
            # 全局消息 (Global message)
            await self.connection_manager.broadcast_to_all(message, exclude_connections=[connection_id])

    async def handle_notification(self, connection_id: str, message: WebSocketMessage):
        """
        处理通知消息 (Handle notification message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 通知消息 (Notification message)
        """
        logger.info(f"处理通知消息 (Handling notification message): {connection_id}")
        
        # 通知消息通常由系统发送，这里记录日志 (Notification messages are usually sent by system, log here)
        if isinstance(message.content, dict) and "type" in message.content:
            notification_type = message.content["type"]
            logger.info(f"通知类型 (Notification type): {notification_type}")

    async def handle_command(self, connection_id: str, message: WebSocketMessage):
        """
        处理命令消息 (Handle command message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 命令消息 (Command message)
        """
        logger.info(f"处理命令消息 (Handling command message): {connection_id}")
        
        if not isinstance(message.content, dict) or "command" not in message.content:
            error_message = WebSocketMessage(
                type=MessageType.ERROR,
                content={"error": "无效的命令格式 (Invalid command format)"},
                sender_id="system",
                receiver_id=None,
                room_id=None,
                timestamp=datetime.utcnow()
            )
            await self.connection_manager.send_to_connection(connection_id, error_message)
            return

        command = message.content["command"]
        args = message.content.get("args", {})
        
        # 处理内置命令 (Handle built-in commands)
        if command == "join_room":
            await self._handle_join_room_command(connection_id, args)
        elif command == "leave_room":
            await self._handle_leave_room_command(connection_id, args)
        elif command == "create_room":
            await self._handle_create_room_command(connection_id, args)
        elif command == "list_rooms":
            await self._handle_list_rooms_command(connection_id, args)
        elif command == "get_connection_info":
            await self._handle_get_connection_info_command(connection_id, args)
        else:
            # 查找自定义命令处理器 (Look for custom command handler)
            handler = self.command_handlers.get(command)
            if handler:
                await handler(connection_id, message, args)
            else:
                error_message = WebSocketMessage(
                    type=MessageType.ERROR,
                    content={"error": f"未知命令 (Unknown command): {command}"},
                    sender_id="system",
                    receiver_id=None,
                    room_id=None,
                    timestamp=datetime.utcnow()
                )
                await self.connection_manager.send_to_connection(connection_id, error_message)

    async def handle_data(self, connection_id: str, message: WebSocketMessage):
        """
        处理数据消息 (Handle data message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 数据消息 (Data message)
        """
        logger.info(f"处理数据消息 (Handling data message): {connection_id}")
        
        # 数据消息可以用于传输任意结构化数据 (Data messages can be used to transmit arbitrary structured data)
        # 这里可以根据具体业务需求进行处理 (Process according to specific business requirements)
        
        # 记录数据消息的基本信息 (Log basic info of data message)
        if isinstance(message.content, dict) and "data_type" in message.content:
            data_type = message.content["data_type"]
            logger.info(f"数据类型 (Data type): {data_type}")

    async def handle_ai_response(self, connection_id: str, message: WebSocketMessage):
        """
        处理 AI 响应消息 (Handle AI response message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: AI 响应消息 (AI response message)
        """
        logger.info(f"处理 AI 响应消息 (Handling AI response message): {connection_id}")
        
        # AI 响应消息通常发送给特定用户或房间 (AI response messages are usually sent to specific users or rooms)
        if message.receiver_id:
            await self.connection_manager.send_to_user(message.receiver_id, message)
        elif message.room_id:
            await self.connection_manager.broadcast_to_room(message.room_id, message)
        else:
            await self.connection_manager.send_to_connection(connection_id, message)

    async def handle_ai_thinking(self, connection_id: str, message: WebSocketMessage):
        """
        处理 AI 思考消息 (Handle AI thinking message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: AI 思考消息 (AI thinking message)
        """
        logger.info(f"处理 AI 思考消息 (Handling AI thinking message): {connection_id}")
        
        # AI 思考消息表示 AI 正在处理请求 (AI thinking messages indicate AI is processing request)
        # 可以显示加载状态或进度信息 (Can display loading status or progress information)

    async def handle_ai_error(self, connection_id: str, message: WebSocketMessage):
        """
        处理 AI 错误消息 (Handle AI error message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: AI 错误消息 (AI error message)
        """
        logger.error(f"处理 AI 错误消息 (Handling AI error message): {connection_id}")
        
        # AI 错误消息表示 AI 处理过程中出现了错误 (AI error messages indicate errors during AI processing)
        # 应该通知用户并记录错误日志 (Should notify user and log error)

    # 内置命令处理方法 (Built-in command handling methods)
    
    async def _handle_join_room_command(self, connection_id: str, args: Dict[str, Any]):
        """处理加入房间命令 (Handle join room command)"""
        room_id = args.get("room_id")
        if not room_id:
            error_message = WebSocketMessage(
                type=MessageType.ERROR,
                content={"error": "缺少房间ID参数 (Missing room_id parameter)"},
                sender_id="system",
                receiver_id=None,
                room_id=None,
                timestamp=datetime.utcnow()
            )
            await self.connection_manager.send_to_connection(connection_id, error_message)
            return

        success = await self.connection_manager.join_room(connection_id, room_id)
        
        response_message = WebSocketMessage(
            type=MessageType.COMMAND,
            content={
                "command": "join_room_response",
                "success": success,
                "room_id": room_id,
                "message": f"成功加入房间 (Successfully joined room): {room_id}" if success else f"加入房间失败 (Failed to join room): {room_id}"
            },
            sender_id="system",
            receiver_id=None,
            room_id=None,
            timestamp=datetime.utcnow()
        )
        
        await self.connection_manager.send_to_connection(connection_id, response_message)

    async def _handle_leave_room_command(self, connection_id: str, args: Dict[str, Any]):
        """处理离开房间命令 (Handle leave room command)"""
        room_id = args.get("room_id")
        if not room_id:
            error_message = WebSocketMessage(
                type=MessageType.ERROR,
                content={"error": "缺少房间ID参数 (Missing room_id parameter)"},
                sender_id="system",
                receiver_id=None,
                room_id=None,
                timestamp=datetime.utcnow()
            )
            await self.connection_manager.send_to_connection(connection_id, error_message)
            return

        success = await self.connection_manager.leave_room(connection_id, room_id)
        
        response_message = WebSocketMessage(
            type=MessageType.COMMAND,
            content={
                "command": "leave_room_response",
                "success": success,
                "room_id": room_id,
                "message": f"成功离开房间 (Successfully left room): {room_id}" if success else f"离开房间失败 (Failed to leave room): {room_id}"
            },
            sender_id="system",
            receiver_id=None,
            room_id=None,
            timestamp=datetime.utcnow()
        )
        
        await self.connection_manager.send_to_connection(connection_id, response_message)

    async def _handle_create_room_command(self, connection_id: str, args: Dict[str, Any]):
        """处理创建房间命令 (Handle create room command)"""
        room_id = args.get("room_id")
        room_name = args.get("room_name", room_id)
        
        if not room_id:
            error_message = WebSocketMessage(
                type=MessageType.ERROR,
                content={"error": "缺少房间ID参数 (Missing room_id parameter)"},
                sender_id="system",
                receiver_id=None,
                room_id=None,
                timestamp=datetime.utcnow()
            )
            await self.connection_manager.send_to_connection(connection_id, error_message)
            return

        # 获取创建者信息 (Get creator info)
        conn_info = await self.connection_manager.get_connection_info(connection_id)
        created_by = conn_info.user_info.user_id if conn_info and conn_info.user_info else None

        room_info = RoomInfo(
            room_id=room_id,
            name=room_name,
            description=args.get("description"),
            created_by=created_by,
            max_members=args.get("max_members"),
            is_private=args.get("is_private", False)
        )

        success = await self.connection_manager.create_room(room_info)
        
        response_message = WebSocketMessage(
            type=MessageType.COMMAND,
            content={
                "command": "create_room_response",
                "success": success,
                "room_info": room_info.model_dump() if success else None,
                "message": f"成功创建房间 (Successfully created room): {room_id}" if success else f"创建房间失败 (Failed to create room): {room_id}"
            },
            sender_id="system",
            receiver_id=None,
            room_id=None,
            timestamp=datetime.utcnow()
        )
        
        await self.connection_manager.send_to_connection(connection_id, response_message)

    async def _handle_list_rooms_command(self, connection_id: str, args: Dict[str, Any]):
        """处理列出房间命令 (Handle list rooms command)"""
        rooms_info = []
        for room_id, room_info in self.connection_manager.rooms.items():
            member_count = len(await self.connection_manager.get_room_members(room_id))
            rooms_info.append({
                "room_id": room_id,
                "name": room_info.name,
                "description": room_info.description,
                "member_count": member_count,
                "max_members": room_info.max_members,
                "is_private": room_info.is_private,
                "created_at": room_info.created_at.isoformat()
            })

        response_message = WebSocketMessage(
            type=MessageType.COMMAND,
            content={
                "command": "list_rooms_response",
                "rooms": rooms_info,
                "total_count": len(rooms_info)
            },
            sender_id="system",
            receiver_id=None,
            room_id=None,
            timestamp=datetime.utcnow()
        )
        
        await self.connection_manager.send_to_connection(connection_id, response_message)

    async def _handle_get_connection_info_command(self, connection_id: str, args: Dict[str, Any]):
        """处理获取连接信息命令 (Handle get connection info command)"""
        conn_info = await self.connection_manager.get_connection_info(connection_id)
        
        if conn_info:
            info_data = {
                "connection_id": conn_info.connection_id,
                "status": conn_info.status,
                "connected_at": conn_info.connected_at.isoformat(),
                "rooms": conn_info.rooms,
                "user_info": conn_info.user_info.model_dump() if conn_info.user_info else None
            }
        else:
            info_data = None

        response_message = WebSocketMessage(
            type=MessageType.COMMAND,
            content={
                "command": "get_connection_info_response",
                "connection_info": info_data
            },
            sender_id="system",
            receiver_id=None,
            room_id=None,
            timestamp=datetime.utcnow()
        )
        
        await self.connection_manager.send_to_connection(connection_id, response_message)

    def register_command_handler(self, command: str, handler: callable):
        """
        注册自定义命令处理器 (Register custom command handler)
        
        Args:
            command: 命令名称 (Command name)
            handler: 处理器函数 (Handler function)
        """
        self.command_handlers[command] = handler
        logger.info(f"已注册自定义命令处理器 (Custom command handler registered): {command}")

    def unregister_command_handler(self, command: str):
        """
        取消注册自定义命令处理器 (Unregister custom command handler)
        
        Args:
            command: 命令名称 (Command name)
        """
        if command in self.command_handlers:
            del self.command_handlers[command]
            logger.info(f"已取消注册自定义命令处理器 (Custom command handler unregistered): {command}")


# 创建默认消息处理器实例的工厂函数 (Factory function to create default message handler instance)
def create_message_handler(connection_manager: WebSocketConnectionManager) -> WebSocketMessageHandler:
    """
    创建消息处理器实例 (Create message handler instance)
    
    Args:
        connection_manager: WebSocket 连接管理器 (WebSocket connection manager)
        
    Returns:
        WebSocketMessageHandler: 消息处理器实例 (Message handler instance)
    """
    return WebSocketMessageHandler(connection_manager) 