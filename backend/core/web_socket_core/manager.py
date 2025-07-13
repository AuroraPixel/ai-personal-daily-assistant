"""
WebSocket 连接管理器 (WebSocket Connection Manager)
负责管理所有 WebSocket 连接、房间、消息广播等核心功能
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from fastapi import WebSocket
import weakref

from .models import (
    ConnectionInfo, 
    ConnectionStatus, 
    UserInfo, 
    WebSocketMessage, 
    MessageType, 
    RoomInfo, 
    BroadcastMessage,
    WebSocketError
)

# 配置日志 (Configure logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """
    WebSocket 连接管理器 (WebSocket Connection Manager)
    
    功能包括 (Features include):
    - 连接管理 (Connection management)
    - 房间管理 (Room management) 
    - 消息广播 (Message broadcasting)
    - 心跳检测 (Heartbeat detection)
    - 连接状态监控 (Connection status monitoring)
    """
    
    def __init__(self):
        """初始化连接管理器 (Initialize connection manager)"""
        # 活跃连接字典: connection_id -> WebSocket (Active connections)
        self.active_connections: Dict[str, WebSocket] = {}
        
        # 连接信息字典: connection_id -> ConnectionInfo (Connection information)
        self.connection_info: Dict[str, ConnectionInfo] = {}
        
        # 用户连接映射: user_id -> Set[connection_id] (User to connections mapping)
        self.user_connections: Dict[str, Set[str]] = {}
        
        # 房间连接映射: room_id -> Set[connection_id] (Room to connections mapping)
        self.room_connections: Dict[str, Set[str]] = {}
        
        # 房间信息字典: room_id -> RoomInfo (Room information)
        self.rooms: Dict[str, RoomInfo] = {}
        
        # 心跳检测任务 (Heartbeat task)
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # 心跳间隔（秒）(Heartbeat interval in seconds)
        self.heartbeat_interval: int = 30
        
        # 连接超时时间（秒）(Connection timeout in seconds)
        self.connection_timeout: int = 90
        
        # 消息处理器字典: message_type -> handler (Message handlers)
        self.message_handlers: Dict[MessageType, Any] = {}
        
        logger.info("WebSocket 连接管理器已初始化 (WebSocket Connection Manager initialized)")

    async def connect(
        self, 
        websocket: WebSocket, 
        connection_id: Optional[str] = None,
        user_info: Optional[UserInfo] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        接受新的 WebSocket 连接 (Accept new WebSocket connection)
        
        Args:
            websocket: WebSocket 连接对象 (WebSocket connection object)
            connection_id: 可选的连接ID (Optional connection ID)
            user_info: 用户信息 (User information)
            metadata: 额外的连接元数据 (Additional connection metadata)
            
        Returns:
            str: 连接ID (Connection ID)
        """
        await websocket.accept()
        
        # 创建连接信息 (Create connection information)
        conn_info = ConnectionInfo(
            connection_id=connection_id or str(uuid.uuid4()),
            user_info=user_info,
            status=ConnectionStatus.CONNECTED,
            last_ping=None,
            ip_address=None,
            user_agent=None,
            metadata=metadata or {}
        )
        
        # 存储连接 (Store connection)
        self.active_connections[conn_info.connection_id] = websocket
        self.connection_info[conn_info.connection_id] = conn_info
        
        # 如果有用户信息，建立用户连接映射 (Map user to connection if user info provided)
        if user_info and user_info.user_id:
            if user_info.user_id not in self.user_connections:
                self.user_connections[user_info.user_id] = set()
            self.user_connections[user_info.user_id].add(conn_info.connection_id)
        
        # 启动心跳检测（如果还没启动）(Start heartbeat if not already running)
        if self.heartbeat_task is None:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # 发送连接成功消息 (Send connection success message)
        await self.send_to_connection(
            conn_info.connection_id,
            WebSocketMessage(
                type=MessageType.CONNECT,
                content={"status": "connected", "connection_id": conn_info.connection_id},
                timestamp=datetime.utcnow()
            )
        )
        
        logger.info(f"新连接已建立 (New connection established): {conn_info.connection_id}")
        return conn_info.connection_id

    async def disconnect(self, connection_id: str, code: int = 1000):
        """
        断开 WebSocket 连接 (Disconnect WebSocket connection)
        
        Args:
            connection_id: 连接ID (Connection ID)
            code: 断开连接代码 (Disconnection code)
        """
        if connection_id not in self.active_connections:
            logger.warning(f"尝试断开不存在的连接 (Trying to disconnect non-existent connection): {connection_id}")
            return
        
        # 获取连接信息 (Get connection information)
        conn_info = self.connection_info.get(connection_id)
        
        # 从房间中移除连接 (Remove connection from rooms)
        if conn_info:
            for room_id in conn_info.rooms.copy():
                await self.leave_room(connection_id, room_id)
            
            # 从用户连接映射中移除 (Remove from user connections mapping)
            if conn_info.user_info and conn_info.user_info.user_id:
                user_id = conn_info.user_info.user_id
                if user_id in self.user_connections:
                    self.user_connections[user_id].discard(connection_id)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]
        
        # 移除连接 (Remove connection)
        websocket = self.active_connections.pop(connection_id, None)
        self.connection_info.pop(connection_id, None)
        
        # 关闭 WebSocket 连接 (Close WebSocket connection)
        if websocket:
            try:
                await websocket.close(code=code)
            except Exception as e:
                logger.error(f"关闭连接时发生错误 (Error closing connection): {e}")
        
        logger.info(f"连接已断开 (Connection disconnected): {connection_id}")
        
        # 如果没有活跃连接，停止心跳检测 (Stop heartbeat if no active connections)
        if not self.active_connections and self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None

    async def send_to_connection(self, connection_id: str, message: WebSocketMessage) -> bool:
        """
        向指定连接发送消息 (Send message to specific connection)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 要发送的消息 (Message to send)
            
        Returns:
            bool: 发送是否成功 (Whether sending was successful)
        """
        websocket = self.active_connections.get(connection_id)
        if not websocket:
            logger.warning(f"连接不存在 (Connection does not exist): {connection_id}")
            return False
        
        try:
            # 将消息转换为JSON格式 (Convert message to JSON format)
            message_data = message.model_dump()
            # 确保datetime字段被正确序列化 (Ensure datetime fields are properly serialized)
            if 'timestamp' in message_data and hasattr(message_data['timestamp'], 'isoformat'):
                message_data['timestamp'] = message_data['timestamp'].isoformat()
            await websocket.send_text(json.dumps(message_data, ensure_ascii=False, default=str))
            return True
        except Exception as e:
            logger.error(f"发送消息失败 (Failed to send message) {connection_id}: {e}")
            # 连接可能已断开，清理连接 (Connection might be broken, clean up)
            await self.disconnect(connection_id)
            return False

    async def send_to_user(self, user_id: str, message: WebSocketMessage) -> int:
        """
        向指定用户的所有连接发送消息 (Send message to all connections of a specific user)
        
        Args:
            user_id: 用户ID (User ID)
            message: 要发送的消息 (Message to send)
            
        Returns:
            int: 成功发送的连接数量 (Number of successful sends)
        """
        connection_ids = self.user_connections.get(user_id, set())
        success_count = 0
        
        for connection_id in connection_ids.copy():
            if await self.send_to_connection(connection_id, message):
                success_count += 1
        
        return success_count

    async def broadcast_to_all(self, message: WebSocketMessage, exclude_connections: Optional[List[str]] = None) -> int:
        """
        向所有连接广播消息 (Broadcast message to all connections)
        
        Args:
            message: 要广播的消息 (Message to broadcast)
            exclude_connections: 要排除的连接ID列表 (Connection IDs to exclude)
            
        Returns:
            int: 成功发送的连接数量 (Number of successful sends)
        """
        exclude_set = set(exclude_connections or [])
        success_count = 0
        
        for connection_id in list(self.active_connections.keys()):
            if connection_id not in exclude_set:
                if await self.send_to_connection(connection_id, message):
                    success_count += 1
        
        return success_count

    async def broadcast_to_room(self, room_id: str, message: WebSocketMessage, exclude_connections: Optional[List[str]] = None) -> int:
        """
        向房间内的所有连接广播消息 (Broadcast message to all connections in a room)
        
        Args:
            room_id: 房间ID (Room ID)
            message: 要广播的消息 (Message to broadcast)
            exclude_connections: 要排除的连接ID列表 (Connection IDs to exclude)
            
        Returns:
            int: 成功发送的连接数量 (Number of successful sends)
        """
        connection_ids = self.room_connections.get(room_id, set())
        exclude_set = set(exclude_connections or [])
        success_count = 0
        
        for connection_id in connection_ids.copy():
            if connection_id not in exclude_set:
                if await self.send_to_connection(connection_id, message):
                    success_count += 1
        
        return success_count

    async def create_room(self, room_info: RoomInfo) -> bool:
        """
        创建新房间 (Create new room)
        
        Args:
            room_info: 房间信息 (Room information)
            
        Returns:
            bool: 创建是否成功 (Whether creation was successful)
        """
        if room_info.room_id in self.rooms:
            logger.warning(f"房间已存在 (Room already exists): {room_info.room_id}")
            return False
        
        self.rooms[room_info.room_id] = room_info
        self.room_connections[room_info.room_id] = set()
        
        logger.info(f"新房间已创建 (New room created): {room_info.room_id}")
        return True

    async def join_room(self, connection_id: str, room_id: str) -> bool:
        """
        连接加入房间 (Connection joins room)
        
        Args:
            connection_id: 连接ID (Connection ID)
            room_id: 房间ID (Room ID)
            
        Returns:
            bool: 加入是否成功 (Whether joining was successful)
        """
        if connection_id not in self.active_connections:
            logger.warning(f"连接不存在 (Connection does not exist): {connection_id}")
            return False
        
        if room_id not in self.rooms:
            logger.warning(f"房间不存在 (Room does not exist): {room_id}")
            return False
        
        # 检查房间成员限制 (Check room member limit)
        room_info = self.rooms[room_id]
        if room_info.max_members and len(self.room_connections[room_id]) >= room_info.max_members:
            logger.warning(f"房间已满 (Room is full): {room_id}")
            return False
        
        # 添加到房间 (Add to room)
        self.room_connections[room_id].add(connection_id)
        
        # 更新连接信息 (Update connection info)
        conn_info = self.connection_info[connection_id]
        if room_id not in conn_info.rooms:
            conn_info.rooms.append(room_id)
        
        logger.info(f"连接加入房间 (Connection joined room): {connection_id} -> {room_id}")
        return True

    async def leave_room(self, connection_id: str, room_id: str) -> bool:
        """
        连接离开房间 (Connection leaves room)
        
        Args:
            connection_id: 连接ID (Connection ID)
            room_id: 房间ID (Room ID)
            
        Returns:
            bool: 离开是否成功 (Whether leaving was successful)
        """
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(connection_id)
        
        # 更新连接信息 (Update connection info)
        if connection_id in self.connection_info:
            conn_info = self.connection_info[connection_id]
            if room_id in conn_info.rooms:
                conn_info.rooms.remove(room_id)
        
        logger.info(f"连接离开房间 (Connection left room): {connection_id} -> {room_id}")
        return True

    async def get_room_members(self, room_id: str) -> List[str]:
        """
        获取房间成员列表 (Get room member list)
        
        Args:
            room_id: 房间ID (Room ID)
            
        Returns:
            List[str]: 房间内的连接ID列表 (List of connection IDs in room)
        """
        return list(self.room_connections.get(room_id, set()))

    async def get_connection_info(self, connection_id: str) -> Optional[ConnectionInfo]:
        """
        获取连接信息 (Get connection information)
        
        Args:
            connection_id: 连接ID (Connection ID)
            
        Returns:
            Optional[ConnectionInfo]: 连接信息 (Connection information)
        """
        return self.connection_info.get(connection_id)

    async def get_user_connections(self, user_id: str) -> List[str]:
        """
        获取用户的所有连接 (Get all connections of a user)
        
        Args:
            user_id: 用户ID (User ID)
            
        Returns:
            List[str]: 连接ID列表 (List of connection IDs)
        """
        return list(self.user_connections.get(user_id, set()))

    async def get_active_connections_count(self) -> int:
        """
        获取活跃连接数量 (Get count of active connections)
        
        Returns:
            int: 活跃连接数量 (Number of active connections)
        """
        return len(self.active_connections)

    async def get_room_count(self) -> int:
        """
        获取房间数量 (Get count of rooms)
        
        Returns:
            int: 房间数量 (Number of rooms)
        """
        return len(self.rooms)

    async def _heartbeat_loop(self):
        """
        心跳检测循环 (Heartbeat detection loop)
        定期检查连接状态并清理超时连接
        """
        while self.active_connections:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._check_connections()
            except asyncio.CancelledError:
                logger.info("心跳检测任务已取消 (Heartbeat task cancelled)")
                break
            except Exception as e:
                logger.error(f"心跳检测发生错误 (Error in heartbeat): {e}")

    async def _check_connections(self):
        """
        检查连接状态 (Check connection status)
        发送心跳并清理超时连接
        """
        current_time = datetime.utcnow()
        timeout_connections = []
        
        for connection_id, conn_info in self.connection_info.items():
            # 检查连接是否超时 (Check if connection timed out)
            if conn_info.last_ping:
                time_since_ping = current_time - conn_info.last_ping
                if time_since_ping.total_seconds() > self.connection_timeout:
                    timeout_connections.append(connection_id)
                    continue
            
            # 发送心跳 (Send ping)
            ping_message = WebSocketMessage(
                type=MessageType.PING,
                content={"timestamp": current_time.isoformat()},
                timestamp=current_time
            )
            
            if not await self.send_to_connection(connection_id, ping_message):
                timeout_connections.append(connection_id)
        
        # 清理超时连接 (Clean up timeout connections)
        for connection_id in timeout_connections:
            logger.warning(f"连接超时，正在断开 (Connection timeout, disconnecting): {connection_id}")
            await self.disconnect(connection_id)

    async def handle_pong(self, connection_id: str):
        """
        处理心跳响应 (Handle pong response)
        
        Args:
            connection_id: 连接ID (Connection ID)
        """
        if connection_id in self.connection_info:
            self.connection_info[connection_id].last_ping = datetime.utcnow()

    def register_message_handler(self, message_type: MessageType, handler: callable):
        """
        注册消息处理器 (Register message handler)
        
        Args:
            message_type: 消息类型 (Message type)
            handler: 处理器函数 (Handler function)
        """
        self.message_handlers[message_type] = handler
        logger.info(f"已注册消息处理器 (Message handler registered): {message_type}")

    async def handle_message(self, connection_id: str, message: WebSocketMessage):
        """
        处理接收到的消息 (Handle received message)
        
        Args:
            connection_id: 连接ID (Connection ID)
            message: 接收到的消息 (Received message)
        """
        handler = self.message_handlers.get(message.type)
        if handler:
            try:
                await handler(connection_id, message)
            except Exception as e:
                logger.error(f"消息处理器执行错误 (Message handler error): {e}")
                error_message = WebSocketMessage(
                    type=MessageType.ERROR,
                    content={"error": "Message handler error", "details": str(e)},
                    timestamp=datetime.utcnow()
                )
                await self.send_to_connection(connection_id, error_message)
        else:
            logger.warning(f"未找到消息处理器 (No handler found for message type): {message.type}")


# 全局连接管理器实例 (Global connection manager instance)
connection_manager = WebSocketConnectionManager() 