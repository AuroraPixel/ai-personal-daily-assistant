"""
WebSocket 核心模块 (WebSocket Core Module)

AI 个人日常助手项目的 WebSocket 核心功能模块
提供完整的 WebSocket 连接管理、消息处理、房间管理等功能

主要组件 (Main Components):
- models: 数据模型定义 (Data model definitions)
- manager: 连接管理器 (Connection manager)
- handler: 消息处理器 (Message handler)
- utils: 工具函数 (Utility functions)

使用示例 (Usage Example):
```python
from backend.core.web_socket_core import (
    connection_manager,
    WebSocketMessageHandler,
    WebSocketMessage,
    MessageType,
    UserInfo
)

# 创建消息处理器 (Create message handler)
handler = WebSocketMessageHandler(connection_manager)

# 创建用户信息 (Create user info)
user = UserInfo(user_id="user123", username="张三")

# 创建消息 (Create message)
message = WebSocketMessage(
    type=MessageType.CHAT,
    content="你好！(Hello!)",
    sender_id="user123"
)
```
"""

# 导入数据模型 (Import data models)
from .models import (
    MessageType,
    ConnectionStatus,
    UserInfo,
    WebSocketMessage,
    ConnectionInfo,
    RoomInfo,
    BroadcastMessage,
    WebSocketError
)

# 导入连接管理器 (Import connection manager)
from .manager import (
    WebSocketConnectionManager,
    connection_manager  # 全局单例实例 (Global singleton instance)
)

# 导入消息处理器 (Import message handler)
from .handler import (
    WebSocketMessageHandler,
    create_message_handler
)

# 导入工具函数 (Import utility functions)
from .utils import (
    generate_connection_id,
    generate_room_id,
    validate_message,
    parse_websocket_message,
    serialize_message,
    extract_query_params,
    validate_user_info,
    create_error_message,
    format_connection_info,
    calculate_connection_duration,
    is_connection_healthy,
    generate_message_hash,
    filter_connections_by_criteria,
    create_system_notification,
    sanitize_user_input,
    get_client_info_from_headers,
    create_message_from_template,
    MESSAGE_TEMPLATES
)

# 模块版本信息 (Module version info)
__version__ = "1.0.0"
__author__ = "AI Personal Daily Assistant Team"

# 导出的公共接口 (Public API exports)
__all__ = [
    # 数据模型 (Data Models)
    "MessageType",
    "ConnectionStatus", 
    "UserInfo",
    "WebSocketMessage",
    "ConnectionInfo",
    "RoomInfo",
    "BroadcastMessage",
    "WebSocketError",
    
    # 核心组件 (Core Components)
    "WebSocketConnectionManager",
    "connection_manager",
    "WebSocketMessageHandler",
    "create_message_handler",
    
    # 工具函数 (Utility Functions)
    "generate_connection_id",
    "generate_room_id",
    "validate_message",
    "parse_websocket_message",
    "serialize_message",
    "extract_query_params",
    "validate_user_info",
    "create_error_message",
    "format_connection_info",
    "calculate_connection_duration",
    "is_connection_healthy",
    "generate_message_hash",
    "filter_connections_by_criteria",
    "create_system_notification",
    "sanitize_user_input",
    "get_client_info_from_headers",
    "create_message_from_template",
    "MESSAGE_TEMPLATES",
    
    # 版本信息 (Version Info)
    "__version__",
    "__author__"
]

# 模块初始化日志 (Module initialization logging)
import logging
logger = logging.getLogger(__name__)
logger.info(f"WebSocket 核心模块已加载 (WebSocket Core Module loaded) - Version {__version__}")

# 快速启动函数 (Quick start functions)
def create_websocket_server_components():
    """
    创建 WebSocket 服务器所需的核心组件 (Create core components for WebSocket server)
    
    Returns:
        tuple: (连接管理器, 消息处理器) (Connection manager, Message handler)
    """
    manager = connection_manager
    handler = create_message_handler(manager)
    
    logger.info("WebSocket 服务器组件已创建 (WebSocket server components created)")
    return manager, handler


def get_default_message_handlers():
    """
    获取默认的消息处理器映射 (Get default message handler mappings)
    
    Returns:
        dict: 消息类型到处理函数的映射 (Message type to handler function mapping)
    """
    manager, handler = create_websocket_server_components()
    return {
        MessageType.PING: handler.handle_ping,
        MessageType.PONG: handler.handle_pong,
        MessageType.CONNECT: handler.handle_connect,
        MessageType.DISCONNECT: handler.handle_disconnect,
        MessageType.CHAT: handler.handle_chat,
        MessageType.NOTIFICATION: handler.handle_notification,
        MessageType.COMMAND: handler.handle_command,
        MessageType.DATA: handler.handle_data,
        MessageType.AI_RESPONSE: handler.handle_ai_response,
        MessageType.AI_THINKING: handler.handle_ai_thinking,
        MessageType.AI_ERROR: handler.handle_ai_error
    }


# 常用配置常量 (Common configuration constants)
class WebSocketConfig:
    """WebSocket 配置常量 (WebSocket configuration constants)"""
    
    # 默认端口 (Default port)
    DEFAULT_PORT = 8000
    
    # 心跳间隔（秒）(Heartbeat interval in seconds)
    HEARTBEAT_INTERVAL = 30
    
    # 连接超时时间（秒）(Connection timeout in seconds)
    CONNECTION_TIMEOUT = 90
    
    # 最大消息长度 (Maximum message length)
    MAX_MESSAGE_LENGTH = 10000
    
    # 最大房间成员数 (Maximum room members)
    MAX_ROOM_MEMBERS = 100
    
    # 支持的消息类型 (Supported message types)
    SUPPORTED_MESSAGE_TYPES = [e.value for e in MessageType]
    
    # 系统用户ID (System user ID)
    SYSTEM_USER_ID = "system"
    
    # 默认房间ID (Default room ID)
    DEFAULT_ROOM_ID = "general"


# 添加配置到导出列表 (Add config to exports)
__all__.append("WebSocketConfig") 