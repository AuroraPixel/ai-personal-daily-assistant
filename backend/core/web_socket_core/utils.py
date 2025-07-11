"""
WebSocket 工具函数 (WebSocket Utility Functions)
提供 WebSocket 相关的实用工具函数，包括消息验证、连接状态检查、数据转换等
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Tuple
from urllib.parse import parse_qs, urlparse
import hashlib
import secrets

from .models import (
    WebSocketMessage, 
    MessageType, 
    UserInfo, 
    ConnectionInfo,
    ConnectionStatus,
    WebSocketError
)

# 配置日志 (Configure logging)
logger = logging.getLogger(__name__)


def generate_connection_id() -> str:
    """
    生成唯一的连接ID (Generate unique connection ID)
    
    Returns:
        str: 连接ID (Connection ID)
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_str = secrets.token_hex(8)
    return f"conn_{timestamp}_{random_str}"


def generate_room_id(room_name: str = "") -> str:
    """
    生成房间ID (Generate room ID)
    
    Args:
        room_name: 房间名称 (Room name)
        
    Returns:
        str: 房间ID (Room ID)
    """
    if room_name:
        # 清理房间名称，只保留字母数字和下划线 (Clean room name, keep only alphanumeric and underscore)
        clean_name = re.sub(r'[^\w]', '_', room_name.lower())
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        return f"room_{clean_name}_{timestamp}"
    else:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_str = secrets.token_hex(6)
        return f"room_{timestamp}_{random_str}"


def validate_message(message_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证 WebSocket 消息格式 (Validate WebSocket message format)
    
    Args:
        message_data: 消息数据字典 (Message data dictionary)
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息) (Is valid, Error message)
    """
    try:
        # 检查必需字段 (Check required fields)
        required_fields = ["type", "content"]
        for field in required_fields:
            if field not in message_data:
                return False, f"缺少必需字段 (Missing required field): {field}"
        
        # 检查消息类型是否有效 (Check if message type is valid)
        if message_data["type"] not in [e.value for e in MessageType]:
            return False, f"无效的消息类型 (Invalid message type): {message_data['type']}"
        
        # 检查内容字段 (Check content field)
        if "content" not in message_data or message_data["content"] is None:
            return False, "消息内容不能为空 (Message content cannot be empty)"
        
        # 检查可选字段的格式 (Check optional fields format)
        if "timestamp" in message_data:
            try:
                datetime.fromisoformat(message_data["timestamp"].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False, "时间戳格式无效 (Invalid timestamp format)"
        
        return True, None
        
    except Exception as e:
        return False, f"消息验证错误 (Message validation error): {str(e)}"


def parse_websocket_message(raw_message: str) -> Tuple[Optional[WebSocketMessage], Optional[str]]:
    """
    解析 WebSocket 原始消息 (Parse WebSocket raw message)
    
    Args:
        raw_message: 原始消息字符串 (Raw message string)
        
    Returns:
        Tuple[Optional[WebSocketMessage], Optional[str]]: (解析后的消息, 错误信息) (Parsed message, Error message)
    """
    try:
        # 解析JSON (Parse JSON)
        message_data = json.loads(raw_message)
        
        # 验证消息格式 (Validate message format)
        is_valid, error_msg = validate_message(message_data)
        if not is_valid:
            return None, error_msg
        
        # 创建WebSocketMessage对象 (Create WebSocketMessage object)
        message = WebSocketMessage(**message_data)
        return message, None
        
    except json.JSONDecodeError as e:
        return None, f"JSON解析错误 (JSON parsing error): {str(e)}"
    except Exception as e:
        return None, f"消息解析错误 (Message parsing error): {str(e)}"


def serialize_message(message: WebSocketMessage) -> str:
    """
    序列化 WebSocket 消息 (Serialize WebSocket message)
    
    Args:
        message: WebSocket 消息对象 (WebSocket message object)
        
    Returns:
        str: 序列化后的JSON字符串 (Serialized JSON string)
    """
    try:
        message_dict = message.model_dump()
        return json.dumps(message_dict, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error(f"消息序列化错误 (Message serialization error): {e}")
        return json.dumps({"error": "序列化失败 (Serialization failed)"})


def extract_query_params(url: str) -> Dict[str, str]:
    """
    从 WebSocket URL 中提取查询参数 (Extract query parameters from WebSocket URL)
    
    Args:
        url: WebSocket 连接URL (WebSocket connection URL)
        
    Returns:
        Dict[str, str]: 查询参数字典 (Query parameters dictionary)
    """
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # 将列表值转换为单个字符串 (Convert list values to single strings)
        result = {}
        for key, value_list in query_params.items():
            result[key] = value_list[0] if value_list else ""
        
        return result
    except Exception as e:
        logger.error(f"URL参数解析错误 (URL parameter parsing error): {e}")
        return {}


def validate_user_info(user_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证用户信息 (Validate user information)
    
    Args:
        user_data: 用户数据字典 (User data dictionary)
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息) (Is valid, Error message)
    """
    try:
        # 检查必需字段 (Check required fields)
        if "user_id" not in user_data or not user_data["user_id"]:
            return False, "用户ID不能为空 (User ID cannot be empty)"
        
        # 验证用户ID格式 (Validate user ID format)
        user_id = user_data["user_id"]
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            return False, "用户ID格式无效，只允许字母、数字、下划线和连字符 (Invalid user ID format)"
        
        # 验证邮箱格式（如果提供）(Validate email format if provided)
        if "email" in user_data and user_data["email"]:
            email = user_data["email"]
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False, "邮箱格式无效 (Invalid email format)"
        
        return True, None
        
    except Exception as e:
        return False, f"用户信息验证错误 (User info validation error): {str(e)}"


def create_error_message(error_code: str, error_message: str, connection_id: Optional[str] = None) -> WebSocketMessage:
    """
    创建错误消息 (Create error message)
    
    Args:
        error_code: 错误代码 (Error code)
        error_message: 错误消息 (Error message)
        connection_id: 连接ID (Connection ID)
        
    Returns:
        WebSocketMessage: 错误消息对象 (Error message object)
    """
    error_content = WebSocketError(
        error_code=error_code,
        error_message=error_message,
        error_type="websocket_error",
        connection_id=connection_id
    )
    
    return WebSocketMessage(
        type=MessageType.ERROR,
        content=error_content.model_dump(),
        sender_id="system",
        receiver_id=None,
        room_id=None,
        timestamp=datetime.utcnow()
    )


def format_connection_info(conn_info: ConnectionInfo) -> Dict[str, Any]:
    """
    格式化连接信息用于传输 (Format connection info for transmission)
    
    Args:
        conn_info: 连接信息对象 (Connection info object)
        
    Returns:
        Dict[str, Any]: 格式化后的连接信息 (Formatted connection info)
    """
    return {
        "connection_id": conn_info.connection_id,
        "status": conn_info.status.value,
        "connected_at": conn_info.connected_at.isoformat(),
        "last_ping": conn_info.last_ping.isoformat() if conn_info.last_ping else None,
        "rooms": conn_info.rooms,
        "user_info": {
            "user_id": conn_info.user_info.user_id,
            "username": conn_info.user_info.username,
            "email": conn_info.user_info.email,
            "roles": conn_info.user_info.roles
        } if conn_info.user_info else None
    }


def calculate_connection_duration(conn_info: ConnectionInfo) -> timedelta:
    """
    计算连接持续时间 (Calculate connection duration)
    
    Args:
        conn_info: 连接信息对象 (Connection info object)
        
    Returns:
        timedelta: 连接持续时间 (Connection duration)
    """
    return datetime.utcnow() - conn_info.connected_at


def is_connection_healthy(conn_info: ConnectionInfo, timeout_seconds: int = 90) -> bool:
    """
    检查连接是否健康 (Check if connection is healthy)
    
    Args:
        conn_info: 连接信息对象 (Connection info object)
        timeout_seconds: 超时秒数 (Timeout in seconds)
        
    Returns:
        bool: 连接是否健康 (Whether connection is healthy)
    """
    if conn_info.status != ConnectionStatus.CONNECTED:
        return False
    
    if conn_info.last_ping:
        time_since_ping = datetime.utcnow() - conn_info.last_ping
        return time_since_ping.total_seconds() <= timeout_seconds
    
    # 如果没有心跳记录，检查连接时间 (If no ping record, check connection time)
    connection_duration = calculate_connection_duration(conn_info)
    return connection_duration.total_seconds() <= timeout_seconds


def generate_message_hash(message: WebSocketMessage) -> str:
    """
    生成消息哈希值用于去重 (Generate message hash for deduplication)
    
    Args:
        message: WebSocket 消息对象 (WebSocket message object)
        
    Returns:
        str: 消息哈希值 (Message hash)
    """
    # 创建消息的唯一标识符 (Create unique identifier for message)
    content_str = json.dumps(message.content, sort_keys=True, ensure_ascii=False)
    hash_input = f"{message.type}_{content_str}_{message.sender_id}_{message.receiver_id}_{message.room_id}"
    
    return hashlib.md5(hash_input.encode('utf-8')).hexdigest()


def filter_connections_by_criteria(
    connections: Dict[str, ConnectionInfo], 
    criteria: Dict[str, Any]
) -> List[str]:
    """
    根据条件筛选连接 (Filter connections by criteria)
    
    Args:
        connections: 连接信息字典 (Connection info dictionary)
        criteria: 筛选条件 (Filter criteria)
        
    Returns:
        List[str]: 符合条件的连接ID列表 (List of matching connection IDs)
    """
    matching_connections = []
    
    for conn_id, conn_info in connections.items():
        match = True
        
        # 检查状态条件 (Check status criteria)
        if "status" in criteria and conn_info.status != criteria["status"]:
            match = False
        
        # 检查用户角色条件 (Check user role criteria)
        if "roles" in criteria and conn_info.user_info:
            required_roles = criteria["roles"]
            if not any(role in conn_info.user_info.roles for role in required_roles):
                match = False
        
        # 检查房间条件 (Check room criteria)
        if "room_id" in criteria:
            if criteria["room_id"] not in conn_info.rooms:
                match = False
        
        # 检查连接时间条件 (Check connection time criteria)
        if "min_connection_time" in criteria:
            min_time = timedelta(seconds=criteria["min_connection_time"])
            if calculate_connection_duration(conn_info) < min_time:
                match = False
        
        if match:
            matching_connections.append(conn_id)
    
    return matching_connections


def create_system_notification(
    notification_type: str, 
    content: Dict[str, Any],
    target_room: Optional[str] = None,
    target_user: Optional[str] = None
) -> WebSocketMessage:
    """
    创建系统通知消息 (Create system notification message)
    
    Args:
        notification_type: 通知类型 (Notification type)
        content: 通知内容 (Notification content)
        target_room: 目标房间ID (Target room ID)
        target_user: 目标用户ID (Target user ID)
        
    Returns:
        WebSocketMessage: 系统通知消息 (System notification message)
    """
    notification_content = {
        "type": notification_type,
        "timestamp": datetime.utcnow().isoformat(),
        **content
    }
    
    return WebSocketMessage(
        type=MessageType.NOTIFICATION,
        content=notification_content,
        sender_id="system",
        receiver_id=target_user,
        room_id=target_room,
        timestamp=datetime.utcnow()
    )


def sanitize_user_input(user_input: str, max_length: int = 1000) -> str:
    """
    清理用户输入 (Sanitize user input)
    
    Args:
        user_input: 用户输入字符串 (User input string)
        max_length: 最大长度限制 (Maximum length limit)
        
    Returns:
        str: 清理后的输入 (Sanitized input)
    """
    if not isinstance(user_input, str):
        return ""
    
    # 移除潜在危险字符 (Remove potentially dangerous characters)
    sanitized = re.sub(r'[<>"\']', '', user_input)
    
    # 限制长度 (Limit length)
    sanitized = sanitized[:max_length]
    
    # 移除首尾空白字符 (Strip whitespace)
    sanitized = sanitized.strip()
    
    return sanitized


def get_client_info_from_headers(headers: Dict[str, str]) -> Dict[str, Optional[str]]:
    """
    从请求头中提取客户端信息 (Extract client info from headers)
    
    Args:
        headers: HTTP 请求头字典 (HTTP headers dictionary)
        
    Returns:
        Dict[str, Optional[str]]: 客户端信息 (Client information)
    """
    return {
        "user_agent": headers.get("user-agent"),
        "origin": headers.get("origin"),
        "host": headers.get("host"),
        "accept_language": headers.get("accept-language"),
        "sec_websocket_protocol": headers.get("sec-websocket-protocol"),
        "sec_websocket_version": headers.get("sec-websocket-version")
    }


# 预定义的消息模板 (Predefined message templates)
MESSAGE_TEMPLATES = {
    "welcome": {
        "type": "welcome",
        "title": "欢迎 (Welcome)",
        "message": "欢迎连接到 AI 个人日常助手！(Welcome to AI Personal Daily Assistant!)"
    },
    "user_joined": {
        "type": "user_joined",
        "title": "用户加入 (User Joined)",
        "message": "{username} 已加入房间 ({username} joined the room)"
    },
    "user_left": {
        "type": "user_left", 
        "title": "用户离开 (User Left)",
        "message": "{username} 已离开房间 ({username} left the room)"
    },
    "room_created": {
        "type": "room_created",
        "title": "房间创建 (Room Created)",
        "message": "房间 {room_name} 已创建 (Room {room_name} has been created)"
    },
    "connection_error": {
        "type": "connection_error",
        "title": "连接错误 (Connection Error)",
        "message": "连接出现错误，请稍后重试 (Connection error, please try again later)"
    }
}


def create_message_from_template(template_name: str, **kwargs) -> Optional[WebSocketMessage]:
    """
    从模板创建消息 (Create message from template)
    
    Args:
        template_name: 模板名称 (Template name)
        **kwargs: 模板变量 (Template variables)
        
    Returns:
        Optional[WebSocketMessage]: 创建的消息对象 (Created message object)
    """
    template = MESSAGE_TEMPLATES.get(template_name)
    if not template:
        logger.warning(f"未找到消息模板 (Message template not found): {template_name}")
        return None
    
    try:
        # 格式化模板内容 (Format template content)
        formatted_content = {}
        for key, value in template.items():
            if isinstance(value, str) and "{" in value:
                formatted_content[key] = value.format(**kwargs)
            else:
                formatted_content[key] = value
        
        return WebSocketMessage(
            type=MessageType.NOTIFICATION,
            content=formatted_content,
            sender_id="system",
            receiver_id=kwargs.get("receiver_id"),
            room_id=kwargs.get("room_id"),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"消息模板处理错误 (Message template processing error): {e}")
        return None 