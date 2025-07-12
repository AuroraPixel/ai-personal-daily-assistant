from __future__ import annotations as _annotations

import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from agents.items import T
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

# Add backend directory to Python path FIRST
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import our custom modules
from core.database_core import DatabaseClient
from agent.personal_assistant_manager import PersonalAssistantManager, PersonalAssistantContext
from agents import (
    Runner,
    InputGuardrailTripwireTriggered,
    MessageOutputItem,
    HandoffOutputItem,
    ItemHelpers,
    Handoff,
    ToolCallItem,
    ToolCallOutputItem,
)

# =========================
# 全局变量
# =========================
# 数据库客户端
db_client: Optional[DatabaseClient] = None
# 个人助手管理器
assistant_manager: Optional[PersonalAssistantManager] = None

# =========================
# 请求体相关
# =========================
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

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
    guardrails: List[GuardrailCheck] = []

# =========================
# 会话存储
# =========================
class ConversationStore:
    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        pass

    def save(self, conversation_id: str, state: Dict[str, Any]):
        pass

class InMemoryConversationStore(ConversationStore):
    _conversations: Dict[str, Dict[str, Any]] = {}

    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return self._conversations.get(conversation_id)

    def save(self, conversation_id: str, state: Dict[str, Any]):
        self._conversations[conversation_id] = state

# TODO: when deploying this app in scale, switch to your own production-ready implementation
conversation_store = InMemoryConversationStore()



# =========================
# 辅助函数
# =========================
# 获取智能体对象
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
# 获取守卫rail名称
# =========================
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
    global db_client, assistant_manager
    
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
            mcp_server_url="http://127.0.0.1:8002/mcp"
        )
        
        # 3. 初始化管理器
        print("⚙️  正在初始化管理器...")
        success = await assistant_manager.initialize()
        
        if success:
            print("🎉 所有服务初始化完成")
        else:
            print("⚠️  服务初始化部分失败，但应用将继续运行")
            
    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        print("⚠️  应用将在有限功能下继续运行")

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
# Main Chat Endpoint
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 基础接口
# =========================
@app.get("/")
async def root():
    """根路径 - 返回API信息"""
    return {
        "message": "AI Personal Daily Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "database": db_client is not None,
            "assistant_manager": assistant_manager is not None and assistant_manager.is_initialized,
            "agents": len(assistant_manager.available_agents) if assistant_manager else 0
        }
    }

# =========================
# 应用启动事件处理器
# =========================
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化所有服务"""
    try:
        await initialize_all_services()
    except Exception as e:
        print(f"❌ 服务初始化过程中发生错误: {e}")
        print("⚠️  应用将继续启动，但某些功能可能不可用")
        print("💡 请检查MCP服务器是否在 http://127.0.0.1:8002/mcp 运行")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main chat endpoint for agent orchestration.
    Handles conversation state, agent routing, and guardrail checks.
    """
    # Initialize or retrieve conversation state
    is_new = not req.conversation_id or conversation_store.get(req.conversation_id) is None
    if is_new:
        conversation_id: str = uuid4().hex
        ctx = initialize_context(1)
        current_agent_name = "Triage Agent"  # 默认使用任务调度中心
        state: Dict[str, Any] = {
            "input_items": [],
            "context": ctx,
            "current_agent": current_agent_name,
        }
        if req.message.strip() == "":
            conversation_store.save(conversation_id, state)
            return ChatResponse(
                conversation_id=conversation_id,
                current_agent=current_agent_name,
                messages=[],
                events=[],
                context=ctx.model_dump(),
                agents=_build_agents_list(),
                guardrails=[],
            )
    else:
        conversation_id = req.conversation_id  # type: ignore
        stored_state = conversation_store.get(conversation_id)
        if stored_state is None:
            # 如果找不到会话状态，创建新的
            ctx = initialize_context(1)
            current_agent_name = "Triage Agent"  # 默认使用任务调度中心
            state = {
                "input_items": [],
                "context": ctx,
                "current_agent": current_agent_name,
            }
        else:
            state = stored_state

    current_agent = _get_agent_by_name(state["current_agent"])
    state["input_items"].append({"content": req.message, "role": "user"})
    old_context = state["context"].model_dump().copy()
    guardrail_checks: List[GuardrailCheck] = []

    triage_agent = _get_agent_by_name("Triage Agent")

    try:
        result = await Runner.run(triage_agent, state["input_items"], context=state["context"])
    except InputGuardrailTripwireTriggered as e:
        failed = e.guardrail_result.guardrail
        gr_output = e.guardrail_result.output.output_info
        gr_reasoning = getattr(gr_output, "reasoning", "")
        gr_input = req.message
        gr_timestamp = time.time() * 1000
        for g in current_agent.input_guardrails:
            guardrail_checks.append(GuardrailCheck(
                id=uuid4().hex,
                name=_get_guardrail_name(g),
                input=gr_input,
                reasoning=(gr_reasoning if g == failed else ""),
                passed=(g != failed),
                timestamp=gr_timestamp,
            ))
        refusal = "Sorry, I can only answer questions related to airline travel."
        state["input_items"].append({"role": "assistant", "content": refusal})
        return ChatResponse(
            conversation_id=conversation_id,
            current_agent=current_agent.name,
            messages=[MessageResponse(content=refusal, agent=current_agent.name)],
            events=[],
            context=state["context"].model_dump(),
            agents=_build_agents_list(),
            guardrails=guardrail_checks,
        )

    messages: List[MessageResponse] = []
    events: List[AgentEvent] = []

    for item in result.new_items:
        if isinstance(item, MessageOutputItem):
            text = ItemHelpers.text_message_output(item)
            messages.append(MessageResponse(content=text, agent=item.agent.name))
            events.append(AgentEvent(id=uuid4().hex, type="message", agent=item.agent.name, content=text))
        # Handle handoff output and agent switching
        elif isinstance(item, HandoffOutputItem):
            # Record the handoff event
            events.append(
                AgentEvent(
                    id=uuid4().hex,
                    type="handoff",
                    agent=item.source_agent.name,
                    content=f"{item.source_agent.name} -> {item.target_agent.name}",
                    metadata={"source_agent": item.source_agent.name, "target_agent": item.target_agent.name},
                )
            )
            # If there is an on_handoff callback defined for this handoff, show it as a tool call
            from_agent = item.source_agent
            to_agent = item.target_agent
            # Find the Handoff object on the source agent matching the target
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
                        events.append(
                            AgentEvent(
                                id=uuid4().hex,
                                type="tool_call",
                                agent=to_agent.name,
                                content=cb_name,
                            )
                        )
            current_agent = item.target_agent
        elif isinstance(item, ToolCallItem):
            tool_name = getattr(item.raw_item, "name", None)
            raw_args = getattr(item.raw_item, "arguments", None)
            tool_args: Any = raw_args
            if isinstance(raw_args, str):
                try:
                    import json
                    tool_args = json.loads(raw_args)
                except Exception:
                    pass
            events.append(
                AgentEvent(
                    id=uuid4().hex,
                    type="tool_call",
                    agent=item.agent.name,
                    content=tool_name or "",
                    metadata={"tool_args": tool_args},
                )
            )
            # If the tool is display_seat_map, send a special message so the UI can render the seat selector.
            if tool_name == "display_seat_map":
                messages.append(
                    MessageResponse(
                        content="DISPLAY_SEAT_MAP",
                        agent=item.agent.name,
                    )
                )
        elif isinstance(item, ToolCallOutputItem):
            events.append(
                AgentEvent(
                    id=uuid4().hex,
                    type="tool_output",
                    agent=item.agent.name,
                    content=str(item.output),
                    metadata={"tool_result": item.output},
                )
            )

    new_context = state["context"].model_dump()
    changes = {k: new_context[k] for k in new_context if old_context.get(k) != new_context[k]}
    if changes:
        events.append(
            AgentEvent(
                id=uuid4().hex,
                type="context_update",
                agent=current_agent.name,
                content="",
                metadata={"changes": changes},
            )
        )

    state["input_items"] = result.to_input_list()
    state["current_agent"] = current_agent.name
    conversation_store.save(conversation_id, state)

    # Build guardrail results: mark failures (if any), and any others as passed
    final_guardrails: List[GuardrailCheck] = []
    for g in getattr(current_agent, "input_guardrails", []):
        name = _get_guardrail_name(g)
        failed = next((gc for gc in guardrail_checks if gc.name == name), None)
        if failed:
            final_guardrails.append(failed)
        else:
            final_guardrails.append(GuardrailCheck(
                id=uuid4().hex,
                name=name,
                input=req.message,
                reasoning="",
                passed=True,
                timestamp=time.time() * 1000,
            ))

    return ChatResponse(
        conversation_id=conversation_id,
        current_agent=current_agent.name,
        messages=messages,
        events=events,
        context=state["context"].model_dump(),
        agents=_build_agents_list(),
        guardrails=final_guardrails,
    )