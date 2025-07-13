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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Path
from fastapi.responses import HTMLResponse
import asyncio
from agent.personal_assistant_manager import PersonalAssistantManager, PersonalAssistantContext
# 导入会话管理器
from agent.agent_session import AgentSessionManager
from core.database_core import DatabaseClient
from typing import Optional
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent
from agents.items import ItemHelpers, MessageOutputItem, HandoffOutputItem, ToolCallItem, ToolCallOutputItem
from agents import Handoff
from pydantic import BaseModel
from typing import List, Dict, Any
from uuid import uuid4

# 导入服务层
from service.services.conversation_service import ConversationService
from service.services.chat_message_service import ChatMessageService

from core.web_socket_core import (
    connection_manager,
    WebSocketMessageHandler,
    WebSocketMessage,
    MessageType,
    UserInfo,
    parse_websocket_message,
    validate_message,
    create_error_message,
    generate_connection_id,
    WebSocketConfig
)

class MessageResponse(BaseModel):
    content: str
    agent: str


class AgentEvent(BaseModel):
    id: str
    type: str
    agent: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None

class GuardrailCheck(BaseModel):
    id: str
    name: str
    input: str
    reasoning: str
    passed: bool
    timestamp: float

class ChatResponse(BaseModel):
    conversation_id: str
    current_agent: str
    messages: List[MessageResponse]
    events: List[AgentEvent]
    context: Dict[str, Any]
    agents: List[Dict[str, Any]]
    raw_response: str
    guardrails: List[GuardrailCheck] = []
    is_finished: bool = False

# =========================
# 全局变量
# =========================
# 数据库客户端
db_client: Optional[DatabaseClient] = None
# 个人助手管理器
assistant_manager: Optional[PersonalAssistantManager] = None
# 会话管理器
session_manager: Optional[AgentSessionManager] = None

# 用户房间映射
user_rooms: Dict[str, str] = {}

# 用户会话映射
user_conversations: Dict[str, str] = {}

def initialize_context(user_id: int) -> PersonalAssistantContext:
    """初始化用户上下文"""
    if assistant_manager is None:
        # 如果管理器未初始化，返回默认上下文
        return PersonalAssistantContext(
            user_id=user_id,
            user_name=f"User {user_id}",
            lat="Unknown",
            lng="Unknown",
            user_preferences={},
            todos=[]
        )
    
    return assistant_manager.create_user_context(user_id)

# =========================
# 构建智能体列表
# =========================
def _build_agents_list() -> List[Dict[str, Any]]:
    """Build a list of all available agents and their metadata."""
    if assistant_manager is None:
        return []
    
    def make_agent_dict(agent):
        return {
            "name": agent.name,
            "description": getattr(agent, "handoff_description", ""),
            "handoffs": [getattr(h, "agent_name", getattr(h, "name", "")) for h in getattr(agent, "handoffs", [])],
            "tools": [getattr(t, "name", getattr(t, "__name__", "")) for t in getattr(agent, "tools", [])],
            "input_guardrails": [_get_guardrail_name(g) for g in getattr(agent, "input_guardrails", [])],
        }
    
    try:
        return [
            make_agent_dict(assistant_manager.get_triage_agent()),
            make_agent_dict(assistant_manager.get_news_agent()),
            make_agent_dict(assistant_manager.get_recipe_agent()),
            make_agent_dict(assistant_manager.get_personal_agent()),
            make_agent_dict(assistant_manager.get_weather_agent()),
        ]
    except Exception:
        return []

# =========================
# 初始化函数
# =========================
async def initialize_all_services():
    """初始化所有服务"""
    global db_client, assistant_manager, session_manager
    
    try:
        print("🚀 开始初始化所有服务...")
        
        # 1. 初始化数据库客户端
        print("📁 正在初始化数据库客户端...")
        db_client = DatabaseClient()
        db_client.initialize()
        db_client.create_tables()
        print("✅ 数据库客户端初始化完成")
        
        # 2. 创建个人助手管理器
        print("🤖 正在创建个人助手管理器...")
        assistant_manager = PersonalAssistantManager(
            db_client=db_client,
            mcp_server_url="http://localhost:8002/mcp"
        )
        
        # 3. 初始化管理器
        print("⚙️  正在初始化管理器...")
        success = await assistant_manager.initialize()
        
        # 4. 创建会话管理器
        print("💬 正在创建会话管理器...")
        session_manager = AgentSessionManager(
            db_client=db_client,
            default_user_id=1,
            max_messages=100
        )
        print("✅ 会话管理器初始化完成")
        
        if success:
            print("🎉 所有服务初始化完成")
        else:
            print("⚠️  服务初始化部分失败，但应用将继续运行")
            
    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        print("⚠️  应用将在有限功能下继续运行")

def _get_guardrail_name(g) -> str:
    """Extract a friendly guardrail name."""
    name_attr = getattr(g, "name", None)
    if isinstance(name_attr, str) and name_attr:
        return name_attr
    guard_fn = getattr(g, "guardrail_function", None)
    if guard_fn is not None and hasattr(guard_fn, "__name__"):
        return guard_fn.__name__.replace("_", " ").title()
    fn_name = getattr(g, "__name__", None)
    if isinstance(fn_name, str) and fn_name:
        return fn_name.replace("_", " ").title()
    return str(g)

def _get_agent_by_name(name: str):
    """Return the agent object by name."""
    if assistant_manager is None:
        raise RuntimeError("Assistant manager not initialized")
    
    try:
        # 映射智能体名称到管理器方法
        agent_mapping = {
            "Triage Agent": assistant_manager.get_triage_agent,
            "Weather Agent": assistant_manager.get_weather_agent,
            "News Agent": assistant_manager.get_news_agent,
            "Recipe Agent": assistant_manager.get_recipe_agent,
            "Personal Assistant Agent": assistant_manager.get_personal_agent,
        }
        
        if name in agent_mapping:
            return agent_mapping[name]()
        else:
            # 默认返回任务调度中心
            return assistant_manager.get_triage_agent()
    except Exception:
        # 如果获取失败，返回任务调度中心
        return assistant_manager.get_triage_agent()

# =========================
# 流式处理函数
# =========================
async def handle_stream_chat(user_id: str, message: str, connection_id: str) -> None:
    """处理流式聊天消息"""
    try:
        # 检查会话管理器是否初始化
        if session_manager is None:
            logger.error("会话管理器未初始化")
            return
        
        # 初始化用户上下文
        ctx = initialize_context(int(user_id))
        triage_agent = _get_agent_by_name("Triage Agent")
        
        # 创建或获取会话 - 使用传入的会话ID或默认会话ID
        conversation_id = user_conversations.get(user_id) or f"user_{user_id}_conversation"
        agent_session = await session_manager.get_session(conversation_id)
        
        if agent_session is None:
            logger.error(f"无法创建或获取会话: {conversation_id}")
            return
        
        # 设置会话上下文
        agent_session.set_context(ctx)
        agent_session.set_current_agent(triage_agent.name)
        
        # 保存用户消息到会话
        await agent_session.save_message(message, "user")
        
        # 获取完整的会话历史（包含新添加的用户消息）
        session_state = agent_session.get_state()
        input_items = session_state.get("input_items", [])
        
        logger.info(f"🔄 用户 {user_id} 会话历史消息数量: {len(input_items)}")
        for i, item in enumerate(input_items):
            logger.debug(f"  {i+1}. [{item.get('role', 'unknown')}]: {item.get('content', '')[:50]}{'...' if len(item.get('content', '')) > 50 else ''}")
        
        # 处理流式响应，传入完整的会话历史
        print(f"🔄 用户 {user_id} 会话历史消息: {input_items}")
        result = Runner.run_streamed(triage_agent, input=input_items, context=ctx)
        
        # 初始化一个ChatResponse对象
        chat_response = ChatResponse(
            conversation_id=conversation_id,
            current_agent=triage_agent.name,
            messages=[],
            raw_response="",
            events=[],
            context=ctx.model_dump(),
            agents=_build_agents_list(),
            guardrails=[]
        )
        
        # 用于收集助手回复的内容
        assistant_messages = []
        
        # 获取用户房间ID
        room_id = user_rooms.get(user_id)
        if not room_id:
            return
            
        async for event in result.stream_events():
            # Handle raw responses event deltas
            if event.type == "raw_response_event":
                # 检查是否是 response.output_text.delta 类型
                if hasattr(event.data, 'type') and event.data.type == 'response.output_text.delta':
                    # 将 delta 内容追加到 raw_response 中
                    if hasattr(event.data, 'delta') and event.data.delta:
                        chat_response.raw_response += event.data.delta
                        
                        # 发送更新的ChatResponse
                        response_message = WebSocketMessage(
                            type=MessageType.AI_RESPONSE,
                            content=chat_response.model_dump(),
                            sender_id="system",
                            receiver_id=None,
                            room_id=room_id
                        )
                        await connection_manager.send_to_connection(connection_id, response_message)
                continue
                
            # When the agent updates, print that
            elif event.type == "agent_updated_stream_event":
                # 更新current_agent
                chat_response.current_agent = event.new_agent.name
                
                # 发送更新的ChatResponse
                response_message = WebSocketMessage(
                    type=MessageType.AI_RESPONSE,
                    content=chat_response.model_dump(),
                    sender_id="system",
                    receiver_id=None,
                    room_id=room_id
                )
                await connection_manager.send_to_connection(connection_id, response_message)
                continue
                
            # When items are generated, print them
            elif event.type == "run_item_stream_event":
                item = event.item
                
                if isinstance(item, MessageOutputItem):
                    # 处理消息输出项
                    text = ItemHelpers.text_message_output(item)
                    message_response = MessageResponse(content=text, agent=item.agent.name)
                    chat_response.messages.append(message_response)
                    
                    # 保存助手消息到会话
                    assistant_messages.append(text)
                    
                    agent_event = AgentEvent(
                        id=uuid4().hex,
                        type="message",
                        agent=item.agent.name,
                        content=text
                    )
                    chat_response.events.append(agent_event)
                    
                    # 发送更新的ChatResponse
                    response_message = WebSocketMessage(
                        type=MessageType.AI_RESPONSE,
                        content=chat_response.model_dump(),
                        sender_id="system",
                        receiver_id=None,
                        room_id=room_id
                    )
                    await connection_manager.send_to_connection(connection_id, response_message)
                    
                elif isinstance(item, HandoffOutputItem):
                    # 处理移交输出项
                    handoff_event = AgentEvent(
                        id=uuid4().hex,
                        type="handoff",
                        agent=item.source_agent.name,
                        content=f"{item.source_agent.name} -> {item.target_agent.name}",
                        metadata={"source_agent": item.source_agent.name, "target_agent": item.target_agent.name}
                    )
                    chat_response.events.append(handoff_event)
                    
                    # 处理handoff回调
                    from_agent = item.source_agent
                    to_agent = item.target_agent
                    ho = next(
                        (h for h in getattr(from_agent, "handoffs", [])
                         if isinstance(h, Handoff) and getattr(h, "agent_name", None) == to_agent.name),
                        None,
                    )
                    if ho:
                        fn = ho.on_invoke_handoff
                        fv = fn.__code__.co_freevars
                        cl = fn.__closure__ or []
                        if "on_handoff" in fv:
                            idx = fv.index("on_handoff")
                            if idx < len(cl) and cl[idx].cell_contents:
                                cb = cl[idx].cell_contents
                                cb_name = getattr(cb, "__name__", repr(cb))
                                callback_event = AgentEvent(
                                    id=uuid4().hex,
                                    type="tool_call",
                                    agent=to_agent.name,
                                    content=cb_name,
                                )
                                chat_response.events.append(callback_event)
                    
                    # 更新current_agent
                    chat_response.current_agent = item.target_agent.name
                    
                    # 发送更新的ChatResponse
                    response_message = WebSocketMessage(
                        type=MessageType.AI_RESPONSE,
                        content=chat_response.model_dump(),
                        sender_id="system",
                        receiver_id=None,
                        room_id=room_id
                    )
                    await connection_manager.send_to_connection(connection_id, response_message)
                    
                elif isinstance(item, ToolCallItem):
                    # 处理工具调用项
                    tool_name = getattr(item.raw_item, "name", None)
                    raw_args = getattr(item.raw_item, "arguments", None)
                    tool_args: Any = raw_args
                    if isinstance(raw_args, str):
                        try:
                            import json
                            tool_args = json.loads(raw_args)
                        except Exception:
                            pass
                    
                    tool_call_event = AgentEvent(
                        id=uuid4().hex,
                        type="tool_call",
                        agent=item.agent.name,
                        content=tool_name or "",
                        metadata={"tool_args": tool_args}
                    )
                    chat_response.events.append(tool_call_event)
                    
                    # 特殊处理display_seat_map
                    if tool_name == "display_seat_map":
                        seat_map_message = MessageResponse(
                            content="DISPLAY_SEAT_MAP",
                            agent=item.agent.name,
                        )
                        chat_response.messages.append(seat_map_message)
                    
                    # 发送更新的ChatResponse
                    response_message = WebSocketMessage(
                        type=MessageType.AI_RESPONSE,
                        content=chat_response.model_dump(),
                        sender_id="system",
                        receiver_id=None,
                        room_id=room_id
                    )
                    await connection_manager.send_to_connection(connection_id, response_message)
                    
                elif isinstance(item, ToolCallOutputItem):
                    # 处理工具调用输出项
                    tool_output_event = AgentEvent(
                        id=uuid4().hex,
                        type="tool_output",
                        agent=item.agent.name,
                        content=str(item.output),
                        metadata={"tool_result": item.output}
                    )
                    chat_response.events.append(tool_output_event)
                    
                    # 发送更新的ChatResponse
                    response_message = WebSocketMessage(
                        type=MessageType.AI_RESPONSE,
                        content=chat_response.model_dump(),
                        sender_id="system",
                        receiver_id=None,
                        room_id=room_id
                    )
                    await connection_manager.send_to_connection(connection_id, response_message)
        
        chat_response.is_finished = True
                    
        # 保存助手的完整回复到会话
        full_assistant_response = ""
        if assistant_messages:
            full_assistant_response = "\n".join(assistant_messages)
            await agent_session.save_message(full_assistant_response, "assistant")
            logger.info(f"✅ 已保存助手回复到会话: {conversation_id}")
        
        # 更新会话状态
        final_state = {
            "input_items": [
                {"content": message, "role": "user"},
                {"content": full_assistant_response, "role": "assistant"}
            ] if assistant_messages else [{"content": message, "role": "user"}],
            "context": ctx,
            "current_agent": chat_response.current_agent
        }
        
        await session_manager.save(conversation_id, final_state)
        logger.info(f"✅ 已保存会话状态到数据库")
        
        # 显示会话信息
        conversation_info = agent_session.get_conversation_info()
        if conversation_info:
            logger.info(f"💬 会话信息: {conversation_info['title']} (消息数: {conversation_info['message_count']})")
        
        # 发送完成消息
        completion_message = WebSocketMessage(
            type=MessageType.AI_RESPONSE,
            content={
                "type": "completion",
                "final_response": chat_response.model_dump(),
                "message": "对话完成"
            },
            sender_id="system",
            receiver_id=None,
            room_id=room_id
        )
        await connection_manager.send_to_connection(connection_id, completion_message)
        
    except Exception as e:
        logger.error(f"流式聊天处理错误: {e}")
        
        # 尝试保存错误信息到会话（如果会话存在）
        try:
            if session_manager is not None:
                conversation_id = f"user_{user_id}_conversation"
                agent_session = await session_manager.get_session(conversation_id)
                if agent_session is not None:
                    error_info = f"处理错误: {str(e)}"
                    await agent_session.save_message(error_info, "assistant")
                    logger.info(f"✅ 已保存错误信息到会话: {conversation_id}")
        except Exception as save_error:
            logger.error(f"保存错误信息到会话失败: {save_error}")
        
        # 发送错误消息
        error_message = WebSocketMessage(
            type=MessageType.AI_ERROR,
            content={
                "error": "流式处理失败",
                "details": str(e)
            },
            sender_id="system",
            receiver_id=None,
            room_id=user_rooms.get(user_id)
        )
        await connection_manager.send_to_connection(connection_id, error_message)

# =========================
# 自定义消息处理器
# =========================
class CustomMessageHandler(WebSocketMessageHandler):
    """自定义消息处理器，支持流式输出"""
    
    async def handle_chat(self, connection_id: str, message: WebSocketMessage):
        """处理聊天消息 - 支持流式输出"""
        logger.info(f"处理流式聊天消息: {connection_id}")
        
        # 获取发送者信息
        conn_info = await self.connection_manager.get_connection_info(connection_id)
        if not conn_info or not conn_info.user_info:
            # 发送错误消息
            error_message = WebSocketMessage(
                type=MessageType.ERROR,
                content={"error": "未认证用户无法发送聊天消息"},
                sender_id="system",
                receiver_id=None,
                room_id=None,
                timestamp=datetime.utcnow()
            )
            await self.connection_manager.send_to_connection(connection_id, error_message)
            return

        # 获取用户ID和消息内容
        user_id = conn_info.user_info.user_id
        message_content = message.content
        
        if isinstance(message_content, dict):
            message_content = message_content.get("message", "")
        
        # 启动流式处理
        await handle_stream_chat(user_id, str(message_content), connection_id)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建自定义消息处理器
custom_message_handler = CustomMessageHandler(connection_manager)

# 全局变量存储消息处理器
message_handlers: Dict[str, Any] = {}

# =========================
# 数据模型定义
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
# 启动时初始化
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("启动 WebSocket 服务...")
    
    # 初始化所有服务
    await initialize_all_services()
    
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
    
    # 关闭会话管理器
    if session_manager is not None:
        try:
            session_manager.close()
            logger.info("✅ 会话管理器已关闭")
        except Exception as session_cleanup_error:
            logger.error(f"⚠️  关闭会话管理器时发生错误: {session_cleanup_error}")
    
    # 关闭数据库连接
    if db_client is not None:
        try:
            db_client.close()
            logger.info("✅ 数据库连接已关闭")
        except Exception as db_cleanup_error:
            logger.error(f"⚠️  关闭数据库连接时发生错误: {db_cleanup_error}")
    
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
    user_id: Optional[str] = Query(None, description="用户ID - 必需"),
    username: Optional[str] = Query(None, description="用户名"),
    room_id: Optional[str] = Query(None, description="房间ID"),
    conversation_id: Optional[str] = Query(None, description="会话ID")
):
    """
    WebSocket 主端点
    处理 WebSocket 连接和消息
    """
    # 验证用户ID
    if not user_id:
        await websocket.close(code=4001, reason="缺少用户ID参数")
        return
    
    connection_id = generate_connection_id()
    
    # 创建用户信息
    user_info = UserInfo(
        user_id=user_id,
        username=username or f"用户_{user_id}",
        email=None,
        avatar=None,
        roles=["user"]
    )
    
    # 存储会话ID到全局映射
    if conversation_id:
        user_conversations[user_id] = conversation_id
    
    # 为用户创建单独的房间
    user_room_id = f"user_{user_id}_room"
    user_rooms[user_id] = user_room_id
    
    logger.info(f"新的 WebSocket 连接请求: {connection_id}, 用户: {user_info}, 房间: {user_room_id}")
    
    try:
        # 检查用户是否已有连接，如果有则清理旧连接
        existing_connections = await connection_manager.get_user_connections(user_id)
        if existing_connections:
            logger.info(f"用户 {user_id} 已有连接，清理旧连接: {existing_connections}")
            for old_conn_id in existing_connections:
                try:
                    await connection_manager.disconnect(old_conn_id, code=1000)
                except Exception as e:
                    logger.warning(f"清理旧连接失败: {e}")
        
        # 建立新连接
        await connection_manager.connect(
            websocket=websocket,
            connection_id=connection_id,
            user_info=user_info
        )
        
        # 创建或获取用户房间
        from core.web_socket_core.models import RoomInfo
        user_room_info = RoomInfo(
            room_id=user_room_id,
            name=f"用户 {user_id} 的私人空间",
            description="用户专用聊天房间",
            created_by=user_id,
            max_members=5,  # 增加房间容量，允许多次连接
            is_private=True
        )
        
        # 尝试创建房间，如果已存在则忽略
        room_created = await connection_manager.create_room(user_room_info)
        if not room_created:
            logger.info(f"房间已存在，直接加入: {user_room_id}")
        
        # 加入房间
        join_success = await connection_manager.join_room(connection_id, user_room_id)
        if not join_success:
            logger.error(f"加入房间失败: {user_room_id}")
            await websocket.close(code=4002, reason="加入房间失败")
            return
        
        # 发送连接成功消息
        welcome_message = WebSocketMessage(
            type=MessageType.CONNECT,
            content={
                "message": "欢迎使用 AI 个人日常助手！",
                "connection_id": connection_id,
                "user_info": user_info.dict(),
                "room_id": user_room_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            sender_id="system",
            receiver_id=None,
            room_id=user_room_id
        )
        
        await connection_manager.send_to_connection(connection_id, welcome_message)
        
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
                    
                    # 设置发送者信息和房间ID
                    message.sender_id = user_info.user_id
                    message.room_id = user_room_id
                    
                    # 使用自定义消息处理器处理聊天消息
                    if message.type == MessageType.CHAT:
                        await custom_message_handler.handle_chat(connection_id, message)
                    else:
                        # 其他消息类型使用默认处理器
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
        # 清理用户房间映射
        if user_id in user_rooms:
            del user_rooms[user_id]
        
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


@app.get("/api/conversations/{user_id}")
async def get_user_conversations(
    user_id: int = Path(..., description="用户ID"),
    status: Optional[str] = Query(None, description="会话状态过滤（active/inactive/archived）"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """
    获取用户的会话列表
    
    Args:
        user_id: 用户ID
        status: 会话状态过滤（可选）
        limit: 返回数量限制
        offset: 偏移量
        
    Returns:
        会话列表响应
    """
    try:
        # 检查数据库客户端是否已初始化
        if db_client is None:
            raise HTTPException(status_code=500, detail="数据库未初始化")
        
        # 创建会话服务
        conversation_service = ConversationService(db_client)
        
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
        
        # 关闭服务
        conversation_service.close()
        
        return ConversationListResponse(
            success=True,
            message=f"成功获取用户 {user_id} 的会话列表",
            data=conversations_data,
            total=total_conversations,
            user_id=user_id
        )
        
    except Exception as e:
        logger.error(f"获取用户会话列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")


@app.get("/api/conversations/{conversation_id_str}/messages")
async def get_conversation_messages(
    conversation_id_str: str = Path(..., description="会话ID字符串"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    order_desc: bool = Query(True, description="是否按创建时间倒序排列")
):
    """
    获取会话的聊天记录
    
    Args:
        conversation_id_str: 会话ID字符串
        limit: 返回数量限制
        offset: 偏移量
        order_desc: 是否按创建时间倒序排列
        
    Returns:
        聊天记录响应
    """
    try:
        # 检查数据库客户端是否已初始化
        if db_client is None:
            raise HTTPException(status_code=500, detail="数据库未初始化")
        
        # 创建服务
        conversation_service = ConversationService(db_client)
        chat_message_service = ChatMessageService(db_client)
        
        # 验证会话是否存在
        conversation = conversation_service.get_conversation_by_id_str(conversation_id_str)
        if not conversation:
            raise HTTPException(status_code=404, detail=f"会话 {conversation_id_str} 不存在")
        
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
        
        # 关闭服务
        conversation_service.close()
        chat_message_service.close()
        
        return ChatMessageResponse(
            success=True,
            message=f"成功获取会话 {conversation_id_str} 的聊天记录",
            data=messages_data,
            total=total_messages,
            conversation_id=conversation_id_str,
            conversation_info=conversation_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话聊天记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取聊天记录失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "main_socket_agent:app",
        host="0.0.0.0",
        port=WebSocketConfig.DEFAULT_PORT,
        log_level="info",
        reload=True
    )
