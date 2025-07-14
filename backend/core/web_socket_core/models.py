"""
WebSocket 数据模型 (WebSocket Data Models)
定义 WebSocket 连接、消息、用户等相关的数据结构
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
import uuid


class MessageType(str, Enum):
    """
    WebSocket 消息类型枚举 (WebSocket Message Type Enum)
    定义不同类型的 WebSocket 消息
    """
    # 系统消息 (System Messages)
    CONNECT = "connect"           # 连接建立 (Connection established)
    DISCONNECT = "disconnect"     # 连接断开 (Connection closed)
    PING = "ping"                # 心跳检测 (Heartbeat ping)
    PONG = "pong"                # 心跳响应 (Heartbeat pong)
    ERROR = "error"              # 错误消息 (Error message)
    
    # 用户消息 (User Messages)
    CHAT = "chat"                # 聊天消息 (Chat message)
    SWITCH_CONVERSATION = "switch_conversation"  # 切换会话 (Switch conversation)
    NOTIFICATION = "notification" # 通知消息 (Notification)
    COMMAND = "command"           # 命令消息 (Command message)
    DATA = "data"                # 数据消息 (Data message)
    
    # AI 助手消息 (AI Assistant Messages)
    AI_RESPONSE = "ai_response"   # AI 响应 (AI response)
    AI_THINKING = "ai_thinking"   # AI 思考中 (AI thinking)
    AI_ERROR = "ai_error"         # AI 错误 (AI error)


class ConnectionStatus(str, Enum):
    """
    连接状态枚举 (Connection Status Enum)
    """
    CONNECTING = "connecting"     # 连接中 (Connecting)
    CONNECTED = "connected"       # 已连接 (Connected)
    DISCONNECTED = "disconnected" # 已断开 (Disconnected)
    RECONNECTING = "reconnecting" # 重连中 (Reconnecting)
    ERROR = "error"              # 错误状态 (Error status)


class UserInfo(BaseModel):
    """
    用户信息模型 (User Information Model)
    存储连接用户的基本信息
    """
    user_id: str = Field(..., description="用户唯一标识 (User unique identifier)")
    username: Optional[str] = Field(None, description="用户名 (Username)")
    email: Optional[str] = Field(None, description="用户邮箱 (User email)")
    avatar: Optional[str] = Field(None, description="用户头像URL (User avatar URL)")
    roles: List[str] = Field(default_factory=list, description="用户角色列表 (User roles)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="用户额外信息 (User metadata)")


class WebSocketMessage(BaseModel):
    """
    WebSocket 消息模型 (WebSocket Message Model)
    定义 WebSocket 消息的统一格式
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="消息唯一标识 (Message ID)")
    type: MessageType = Field(..., description="消息类型 (Message type)")
    content: Union[str, Dict[str, Any], List[Any]] = Field(..., description="消息内容 (Message content)")
    sender_id: Optional[str] = Field(None, description="发送者ID (Sender ID)")
    receiver_id: Optional[str] = Field(None, description="接收者ID (Receiver ID)")
    room_id: Optional[str] = Field(None, description="房间ID (Room ID)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳 (Timestamp)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="消息元数据 (Message metadata)")

    class Config:
        """Pydantic 配置 (Pydantic Configuration)"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ConnectionInfo(BaseModel):
    """
    连接信息模型 (Connection Information Model)
    存储 WebSocket 连接的详细信息
    """
    connection_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="连接唯一标识 (Connection ID)")
    user_info: Optional[UserInfo] = Field(None, description="用户信息 (User information)")
    status: ConnectionStatus = Field(ConnectionStatus.CONNECTING, description="连接状态 (Connection status)")
    connected_at: datetime = Field(default_factory=datetime.utcnow, description="连接时间 (Connected time)")
    last_ping: Optional[datetime] = Field(None, description="最后心跳时间 (Last ping time)")
    ip_address: Optional[str] = Field(None, description="客户端IP地址 (Client IP address)")
    user_agent: Optional[str] = Field(None, description="客户端用户代理 (Client user agent)")
    rooms: List[str] = Field(default_factory=list, description="加入的房间列表 (Joined rooms)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="连接元数据 (Connection metadata)")

    class Config:
        """Pydantic 配置 (Pydantic Configuration)"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class RoomInfo(BaseModel):
    """
    房间信息模型 (Room Information Model)
    管理 WebSocket 房间（群组）信息
    """
    room_id: str = Field(..., description="房间唯一标识 (Room ID)")
    name: str = Field(..., description="房间名称 (Room name)")
    description: Optional[str] = Field(None, description="房间描述 (Room description)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间 (Created time)")
    created_by: Optional[str] = Field(None, description="创建者ID (Creator ID)")
    max_members: Optional[int] = Field(None, description="最大成员数 (Maximum members)")
    is_private: bool = Field(False, description="是否私有房间 (Is private room)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="房间元数据 (Room metadata)")

    class Config:
        """Pydantic 配置 (Pydantic Configuration)"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class BroadcastMessage(BaseModel):
    """
    广播消息模型 (Broadcast Message Model)
    用于群发消息的配置
    """
    message: WebSocketMessage = Field(..., description="要广播的消息 (Message to broadcast)")
    target_type: str = Field(..., description="目标类型: 'all', 'room', 'user' (Target type)")
    target_ids: Optional[List[str]] = Field(None, description="目标ID列表 (Target IDs)")
    exclude_ids: Optional[List[str]] = Field(None, description="排除的ID列表 (Excluded IDs)")
    conditions: Optional[Dict[str, Any]] = Field(None, description="筛选条件 (Filter conditions)")


class WebSocketError(BaseModel):
    """
    WebSocket 错误模型 (WebSocket Error Model)
    定义 WebSocket 错误信息的格式
    """
    error_code: str = Field(..., description="错误代码 (Error code)")
    error_message: str = Field(..., description="错误消息 (Error message)")
    error_type: str = Field("websocket_error", description="错误类型 (Error type)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="错误时间 (Error time)")
    connection_id: Optional[str] = Field(None, description="相关连接ID (Related connection ID)")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="额外错误信息 (Additional error info)")

    class Config:
        """Pydantic 配置 (Pydantic Configuration)"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        } 