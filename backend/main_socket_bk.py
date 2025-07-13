"""
AI 个人日常助手 - WebSocket 服务端
使用 FastAPI 和 web_socket_core 模块实现 WebSocket 服务
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import HTMLResponse

from core.web_socket_core import (
    connection_manager,
    WebSocketMessageHandler,
    WebSocketMessage,
    MessageType,
    UserInfo,
    WebSocketError,
    parse_websocket_message,
    validate_message,
    create_error_message,
    extract_query_params,
    validate_user_info,
    generate_connection_id,
    WebSocketConfig
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建消息处理器
message_handler = WebSocketMessageHandler(connection_manager)

# 全局变量存储消息处理器
message_handlers: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("启动 WebSocket 服务...")
    
    # 启动心跳检测任务
    if not connection_manager.heartbeat_task:
        connection_manager.heartbeat_task = asyncio.create_task(
            connection_manager._heartbeat_loop()
        )
    
    logger.info("WebSocket 服务已启动")
    
    yield
    
    # 关闭时的清理
    logger.info("关闭 WebSocket 服务...")
    
    # 停止心跳检测任务
    if connection_manager.heartbeat_task:
        connection_manager.heartbeat_task.cancel()
        try:
            await connection_manager.heartbeat_task
        except asyncio.CancelledError:
            pass
    
    logger.info("WebSocket 服务已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="AI 个人日常助手 WebSocket 服务",
    description="提供实时通信功能的 WebSocket 服务端",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """根路径 - 返回服务信息"""
    return {
        "service": "AI 个人日常助手 WebSocket 服务",
        "version": "1.0.0",
        "status": "running",
        "websocket_endpoint": "/ws",
        "connections": await connection_manager.get_active_connections_count(),
        "rooms": await connection_manager.get_room_count()
    }


@app.get("/test")
async def test_page():
    """测试页面 - 提供简单的 WebSocket 测试界面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket 测试页面</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>WebSocket 测试页面</h1>
        <div>
            <input type="text" id="userIdInput" placeholder="用户ID (可选)" />
            <input type="text" id="usernameInput" placeholder="用户名 (可选)" />
            <button onclick="connect()">连接</button>
            <button onclick="disconnect()">断开连接</button>
        </div>
        <div>
            <select id="messageType">
                <option value="chat">聊天消息</option>
                <option value="ping">心跳检测</option>
                <option value="command">命令消息</option>
                <option value="data">数据消息</option>
            </select>
            <input type="text" id="messageInput" placeholder="输入消息内容" />
            <button onclick="sendMessage()">发送消息</button>
        </div>
        <div>
            <h3>消息记录:</h3>
            <div id="messages" style="height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;"></div>
        </div>

        <script>
            let ws = null;
            let isConnected = false;

            function connect() {
                if (isConnected) return;
                
                const userId = document.getElementById('userIdInput').value;
                const username = document.getElementById('usernameInput').value;
                
                let wsUrl = `ws://localhost:8000/ws`;
                const params = new URLSearchParams();
                if (userId) params.append('user_id', userId);
                if (username) params.append('username', username);
                
                if (params.toString()) {
                    wsUrl += `?${params.toString()}`;
                }
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    isConnected = true;
                    addMessage('系统', '已连接到 WebSocket 服务器', 'system');
                };
                
                ws.onmessage = function(event) {
                    const message = JSON.parse(event.data);
                    addMessage(message.sender_id || '系统', JSON.stringify(message.content), message.type);
                };
                
                ws.onclose = function(event) {
                    isConnected = false;
                    addMessage('系统', '连接已断开', 'system');
                };
                
                ws.onerror = function(error) {
                    addMessage('系统', '连接错误: ' + error, 'error');
                };
            }

            function disconnect() {
                if (ws && isConnected) {
                    ws.close();
                    isConnected = false;
                }
            }

            function sendMessage() {
                if (!isConnected) {
                    alert('请先连接到 WebSocket 服务器');
                    return;
                }
                
                const messageType = document.getElementById('messageType').value;
                const messageContent = document.getElementById('messageInput').value;
                
                if (!messageContent) {
                    alert('请输入消息内容');
                    return;
                }
                
                const message = {
                    type: messageType,
                    content: messageContent,
                    sender_id: document.getElementById('userIdInput').value || 'test_user',
                    timestamp: new Date().toISOString()
                };
                
                ws.send(JSON.stringify(message));
                document.getElementById('messageInput').value = '';
            }

            function addMessage(sender, content, type) {
                const messages = document.getElementById('messages');
                const messageElement = document.createElement('div');
                messageElement.innerHTML = `
                    <strong>[${type}] ${sender}:</strong> ${content}
                    <small style="color: #666;">(${new Date().toLocaleTimeString()})</small>
                `;
                messages.appendChild(messageElement);
                messages.scrollTop = messages.scrollHeight;
            }

            // 页面加载时自动连接
            window.onload = function() {
                // 可以在这里添加自动连接逻辑
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/status")
async def get_status():
    """获取服务状态信息"""
    return {
        "active_connections": await connection_manager.get_active_connections_count(),
        "total_rooms": await connection_manager.get_room_count(),
        "heartbeat_interval": connection_manager.heartbeat_interval,
        "connection_timeout": connection_manager.connection_timeout,
        "service_uptime": "正在运行"
    }


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: Optional[str] = Query(None, description="用户ID"),
    username: Optional[str] = Query(None, description="用户名"),
    room_id: Optional[str] = Query(None, description="房间ID")
):
    """
    WebSocket 主端点
    处理 WebSocket 连接和消息
    """
    connection_id = generate_connection_id()
    
    # 创建用户信息
    user_info = None
    if user_id or username:
        user_info = UserInfo(
            user_id=user_id or f"user_{connection_id}",
            username=username or f"用户_{connection_id}",
            email=None,
            avatar=None,
            roles=["user"]
        )
    
    logger.info(f"新的 WebSocket 连接请求: {connection_id}, 用户: {user_info}")
    
    try:
        # 建立连接
        await connection_manager.connect(
            websocket=websocket,
            connection_id=connection_id,
            user_info=user_info
        )
        
        # 发送连接成功消息
        welcome_message = WebSocketMessage(
            type=MessageType.CONNECT,
            content={
                "message": "欢迎使用 AI 个人日常助手！",
                "connection_id": connection_id,
                "user_info": user_info.dict() if user_info else None,
                "timestamp": datetime.utcnow().isoformat()
            },
            sender_id="system",
            receiver_id=None,
            room_id=None
        )
        
        await connection_manager.send_to_connection(connection_id, welcome_message)
        
        # 如果指定了房间，自动加入房间
        if room_id:
            await connection_manager.join_room(connection_id, room_id)
            room_message = WebSocketMessage(
                type=MessageType.NOTIFICATION,
                content={
                    "message": f"已加入房间: {room_id}",
                    "room_id": room_id
                },
                sender_id="system",
                receiver_id=None,
                room_id=room_id
            )
            await connection_manager.send_to_connection(connection_id, room_message)
        
        # 消息处理循环
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                logger.debug(f"收到消息 from {connection_id}: {data}")
                
                # 解析消息
                try:
                    message_data = json.loads(data)
                    
                    # 验证消息格式
                    is_valid, error_msg = validate_message(message_data)
                    if not is_valid:
                        error_response = create_error_message(
                            "INVALID_MESSAGE", 
                            error_msg or "消息格式无效",
                            connection_id
                        )
                        await connection_manager.send_to_connection(
                            connection_id, 
                            error_response
                        )
                        continue
                    
                    # 解析消息
                    message, parse_error = parse_websocket_message(data)
                    if message is None:
                        error_response = create_error_message(
                            "PARSE_ERROR",
                            parse_error or "消息解析失败",
                            connection_id
                        )
                        await connection_manager.send_to_connection(
                            connection_id,
                            error_response
                        )
                        continue
                    
                    # 设置发送者信息
                    if user_info:
                        message.sender_id = user_info.user_id
                    
                    # 处理消息
                    await connection_manager.handle_message(connection_id, message)
                    
                except json.JSONDecodeError:
                    logger.error(f"无效的 JSON 消息: {data}")
                    error_response = create_error_message(
                        "INVALID_JSON",
                        "无效的 JSON 格式",
                        connection_id
                    )
                    await connection_manager.send_to_connection(
                        connection_id,
                        error_response
                    )
                except Exception as e:
                    logger.error(f"处理消息时发生错误: {str(e)}")
                    error_response = create_error_message(
                        "MESSAGE_PROCESSING_ERROR",
                        f"消息处理错误: {str(e)}",
                        connection_id
                    )
                    await connection_manager.send_to_connection(
                        connection_id,
                        error_response
                    )
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket 连接断开: {connection_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket 错误: {str(e)}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket 连接错误: {str(e)}")
        
    finally:
        # 断开连接
        await connection_manager.disconnect(connection_id)
        logger.info(f"WebSocket 连接已清理: {connection_id}")


@app.post("/broadcast")
async def broadcast_message(
    message_type: str,
    content: str,
    room_id: Optional[str] = None,
    user_id: Optional[str] = None
):
    """
    广播消息 API
    用于通过 HTTP 接口发送广播消息
    """
    try:
        # 验证消息类型
        if message_type not in [e.value for e in MessageType]:
            raise HTTPException(status_code=400, detail="无效的消息类型")
        
        # 创建消息
        message = WebSocketMessage(
            type=MessageType(message_type),
            content=content,
            sender_id="system",
            receiver_id=None,
            room_id=None
        )
        
        sent_count = 0
        
        # 根据目标发送消息
        if room_id:
            # 发送到指定房间
            sent_count = await connection_manager.broadcast_to_room(room_id, message)
        elif user_id:
            # 发送到指定用户
            sent_count = await connection_manager.send_to_user(user_id, message)
        else:
            # 广播到所有连接
            sent_count = await connection_manager.broadcast_to_all(message)
        
        return {
            "status": "success",
            "message": "消息发送成功",
            "sent_count": sent_count,
            "message_id": message.id
        }
        
    except Exception as e:
        logger.error(f"广播消息错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")


@app.get("/connections")
async def get_connections():
    """获取所有活跃连接信息"""
    connections = []
    for conn_id in connection_manager.active_connections.keys():
        conn_info = await connection_manager.get_connection_info(conn_id)
        if conn_info:
            connections.append(conn_info.dict())
    
    return {
        "total": len(connections),
        "connections": connections
    }


@app.get("/rooms")
async def get_rooms():
    """获取所有房间信息"""
    rooms = []
    for room_id, room_info in connection_manager.rooms.items():
        member_count = len(connection_manager.room_connections.get(room_id, set()))
        rooms.append({
            "room_id": room_id,
            "name": room_info.name,
            "description": room_info.description,
            "member_count": member_count,
            "created_at": room_info.created_at.isoformat(),
            "is_private": room_info.is_private
        })
    
    return {
        "total": len(rooms),
        "rooms": rooms
    }


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "main_socket:app",
        host="0.0.0.0",
        port=WebSocketConfig.DEFAULT_PORT,
        log_level="info",
        reload=True
    )
