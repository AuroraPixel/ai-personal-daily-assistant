"""
系统API模块

包含根路径、测试页面、状态查询等系统相关的API端点
"""

import logging
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# 导入WebSocket核心模块
from core.web_socket_core import connection_manager

# 导入服务管理器
from service.service_manager import service_manager

# 配置日志
logger = logging.getLogger(__name__)

# 创建系统API路由器
system_router = APIRouter(tags=["系统"])

# =========================
# API端点
# =========================

@system_router.get("/")
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

@system_router.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        db_status = "healthy"
        try:
            db_client = service_manager.get_db_client()
            if not db_client:
                db_status = "unhealthy"
        except Exception:
            db_status = "unhealthy"
        
        # 检查向量数据库连接
        vector_status = "healthy"
        try:
            vector_client = service_manager.get_vector_client()
            if not vector_client:
                vector_status = "not_configured"
            else:
                health = vector_client.health_check()
                if health.get('status') != 'healthy':
                    vector_status = "unhealthy"
        except Exception:
            vector_status = "unhealthy"
        
        overall_status = "healthy" if db_status == "healthy" else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": db_status,
                "vector_database": vector_status,
                "websocket": "healthy"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@system_router.get("/test")
async def test_page():
    """测试页面 - 提供简单的 WebSocket 测试界面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI 个人日常助手 WebSocket 测试页面</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-group { margin-bottom: 10px; }
            .form-group label { display: inline-block; width: 100px; }
            .form-group input, .form-group select { width: 200px; padding: 5px; }
            .btn { padding: 8px 16px; margin: 5px; cursor: pointer; }
            .btn-primary { background-color: #007bff; color: white; border: none; }
            .btn-danger { background-color: #dc3545; color: white; border: none; }
            .btn-success { background-color: #28a745; color: white; border: none; }
            .messages { height: 400px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; }
            .message { margin-bottom: 10px; padding: 8px; border-radius: 4px; }
            .message.system { background-color: #e7f3ff; }
            .message.user { background-color: #e7ffe7; }
            .message.ai { background-color: #fff3e0; }
            .message.error { background-color: #ffebee; }
            .timestamp { font-size: 0.8em; color: #666; margin-left: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI 个人日常助手 WebSocket 测试页面</h1>
            
            <div class="form-group">
                <label for="userIdInput">用户ID:</label>
                <input type="text" id="userIdInput" placeholder="输入用户ID (必需)" required />
            </div>
            
            <div class="form-group">
                <label for="usernameInput">用户名:</label>
                <input type="text" id="usernameInput" placeholder="输入用户名 (可选)" />
            </div>
            
            <div class="form-group">
                <button class="btn btn-primary" onclick="connect()">连接</button>
                <button class="btn btn-danger" onclick="disconnect()">断开连接</button>
                <span id="connectionStatus">未连接</span>
            </div>
            
            <div class="form-group">
                <label for="messageInput">消息:</label>
                <input type="text" id="messageInput" placeholder="输入聊天消息" style="width: 400px;" />
                <button class="btn btn-success" onclick="sendChatMessage()">发送聊天消息</button>
            </div>
            
            <div>
                <h3>消息记录:</h3>
                <div id="messages" class="messages"></div>
            </div>
        </div>

        <script>
            let ws = null;
            let isConnected = false;
            let currentChatResponse = null;

            function connect() {
                if (isConnected) return;
                
                const userId = document.getElementById('userIdInput').value;
                const username = document.getElementById('usernameInput').value;
                
                if (!userId) {
                    alert('请输入用户ID');
                    return;
                }
                
                let wsUrl = `ws://localhost:8000/ws`;
                const params = new URLSearchParams();
                params.append('user_id', userId);
                if (username) params.append('username', username);
                
                wsUrl += `?${params.toString()}`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    isConnected = true;
                    document.getElementById('connectionStatus').textContent = '已连接';
                    document.getElementById('connectionStatus').style.color = 'green';
                    addMessage('系统', '已连接到 WebSocket 服务器', 'system');
                };
                
                ws.onmessage = function(event) {
                    const message = JSON.parse(event.data);
                    handleMessage(message);
                };
                
                ws.onclose = function(event) {
                    isConnected = false;
                    document.getElementById('connectionStatus').textContent = '未连接';
                    document.getElementById('connectionStatus').style.color = 'red';
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

            function sendChatMessage() {
                if (!isConnected) {
                    alert('请先连接到 WebSocket 服务器');
                    return;
                }
                
                const messageContent = document.getElementById('messageInput').value;
                
                if (!messageContent) {
                    alert('请输入消息内容');
                    return;
                }
                
                const message = {
                    type: 'chat',
                    content: messageContent,
                    timestamp: new Date().toISOString()
                };
                
                ws.send(JSON.stringify(message));
                addMessage('用户', messageContent, 'user');
                document.getElementById('messageInput').value = '';
            }

            function handleMessage(message) {
                if (message.type === 'ai_response') {
                    handleAIResponse(message.content);
                } else if (message.type === 'ai_error') {
                    addMessage('AI 错误', JSON.stringify(message.content), 'error');
                } else if (message.type === 'connect') {
                    addMessage('系统', message.content.message, 'system');
                } else {
                    addMessage('系统', JSON.stringify(message.content), 'system');
                }
            }

            function handleAIResponse(content) {
                if (typeof content === 'object') {
                    // 处理流式响应 - 显示完整的原始数据
                    if (content.type === 'completion') {
                        addMessage('AI 完成', '对话完成', 'ai');
                        displayRawChatResponse('最终响应', content.final_response);
                    } else {
                        // 更新当前响应 - 显示完整的原始数据
                        currentChatResponse = content;
                        displayRawChatResponse('流式响应', content);
                    }
                } else {
                    addMessage('AI', content, 'ai');
                }
            }

            function displayRawChatResponse(title, chatResponse) {
                const messagesContainer = document.getElementById('messages');
                let streamingDiv = document.getElementById('streaming-response');
                
                if (!streamingDiv) {
                    streamingDiv = document.createElement('div');
                    streamingDiv.id = 'streaming-response';
                    streamingDiv.className = 'message ai';
                    streamingDiv.style.fontFamily = 'monospace';
                    streamingDiv.style.fontSize = '12px';
                    streamingDiv.style.whiteSpace = 'pre-wrap';
                    streamingDiv.style.wordBreak = 'break-all';
                    messagesContainer.appendChild(streamingDiv);
                }
                
                // 显示完整的原始 ChatResponse 数据
                const timestamp = new Date().toLocaleTimeString();
                const rawJson = JSON.stringify(chatResponse, null, 2);
                
                streamingDiv.innerHTML = `
                    <strong>🔍 ${title} [${timestamp}]</strong><br>
                    <strong>原始 ChatResponse 数据:</strong><br>
                    <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; max-height: 400px; overflow-y: auto;">
                        ${rawJson}
                    </div>
                `;
                
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            function addMessage(sender, content, type) {
                const messages = document.getElementById('messages');
                const messageElement = document.createElement('div');
                messageElement.className = `message ${type}`;
                messageElement.innerHTML = `
                    <strong>${sender}:</strong> ${content}
                    <span class="timestamp">${new Date().toLocaleTimeString()}</span>
                `;
                messages.appendChild(messageElement);
                messages.scrollTop = messages.scrollHeight;
            }

            // 支持回车键发送消息
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendChatMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@system_router.get("/status")
async def get_status():
    """获取服务状态信息（优化版本）"""
    # 获取服务管理器统计信息
    service_stats = service_manager.get_stats()
    
    return {
        "active_connections": await connection_manager.get_active_connections_count(),
        "total_rooms": await connection_manager.get_room_count(),
        "heartbeat_interval": connection_manager.heartbeat_interval,
        "connection_timeout": connection_manager.connection_timeout,
        "service_uptime": "正在运行",
        "service_manager": service_stats
    } 