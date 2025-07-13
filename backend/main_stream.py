"""
AI 个人日常助手 - 主程序 (AI Personal Daily Assistant - Main Program)

启动 WebSocket 服务器和相关服务 (Start WebSocket server and related services)
"""


import asyncio
from agent.personal_assistant_manager import PersonalAssistantManager, PersonalAssistantContext
from core.database_core import DatabaseClient
from typing import Optional
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent
from agents.items import ItemHelpers, MessageOutputItem, HandoffOutputItem, ToolCallItem, ToolCallOutputItem
from agents import Handoff
from pydantic import BaseModel
from typing import List, Dict, Any
from uuid import uuid4

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

# =========================
# 全局变量
# =========================
# 数据库客户端
db_client: Optional[DatabaseClient] = None
# 个人助手管理器
assistant_manager: Optional[PersonalAssistantManager] = None

# 消息管理器
session: Optional[MessageSession] = None


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
            mcp_server_url="http://localhost:8002/mcp"
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


async def main():
    print("�� 正在启动AI个人日常助手...")
    
    try:
        await initialize_all_services()
        ctx = initialize_context(1)
        triage_agent = _get_agent_by_name("Triage Agent")
        
        # 处理流式响应
        result = Runner.run_streamed(triage_agent, input="我明天想去巴黎游玩给出出行建议（自己转为经纬）", context=ctx)
        
        # 使用异步迭代器处理事件流
        # 初始化一个ChatResponse对象
        chat_response = ChatResponse(
            conversation_id=uuid4().hex,
            current_agent=triage_agent.name,
            messages=[],
            raw_response="",
            events=[],
            context=ctx.model_dump(),
            agents=[],
            guardrails=[]
        )
        
        async for event in result.stream_events():
            # Handle raw responses event deltas
            if event.type == "raw_response_event":
                print(f"Raw response event:{event.data}")
                # 检查是否是 response.output_text.delta 类型
                if hasattr(event.data, 'type') and event.data.type == 'response.output_text.delta':
                    # 将 delta 内容追加到 raw_response 中
                    if hasattr(event.data, 'delta') and event.data.delta:
                        chat_response.raw_response += event.data.delta
                        print(f"追加 delta 到 raw_response: '{event.data.delta}'")
                        print(f"当前 raw_response: '{chat_response.raw_response}'")
                print("\n=================\n")
                continue
            # When the agent updates, print that
            elif event.type == "agent_updated_stream_event":
                #print(f"Agent updated: {event.new_agent.name}")
                # 更新current_agent
                chat_response.current_agent = event.new_agent.name
                print(f"更新后的ChatResponse: {chat_response.model_dump()}")
                print("\n=================\n")
                continue
            # When items are generated, print them
            elif event.type == "run_item_stream_event":
                item = event.item
                
                if isinstance(item, MessageOutputItem):
                    # 处理消息输出项
                    text = ItemHelpers.text_message_output(item)
                    message_response = MessageResponse(content=text, agent=item.agent.name)
                    chat_response.messages.append(message_response)
                    
                    agent_event = AgentEvent(
                        id=uuid4().hex,
                        type="message",
                        agent=item.agent.name,
                        content=text
                    )
                    chat_response.events.append(agent_event)
                    #print(f"-- Message output:\n {text}")
                    print(f"更新后的ChatResponse: {chat_response.model_dump()}")
                    print("\n=================\n")
                    
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
                    #print(f"-- Handoff: {item.source_agent.name} -> {item.target_agent.name}")
                    print(f"更新后的ChatResponse: {chat_response.model_dump()}")
                    print("\n=================\n")
                    
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
                    
                    #print(f"-- Tool was called: {tool_name} by {item.agent.name}")
                    print(f"更新后的ChatResponse: {chat_response.model_dump()}")
                    print("\n=================\n")
                    
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
                    #print(f"-- Tool output: {item.output}")
                    print(f"更新后的ChatResponse: {chat_response.model_dump()}")
                    print("\n=================\n")
                    
                else:
                    print(f"-- Other event: {item.type}")
                    
            # Ignore other event types

        print("=== Run complete ===")
                
    except KeyboardInterrupt:
        print("\n\n⏹️  程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 基本的资源清理
        print("\n🏁 程序结束")
        if db_client is not None:
            try:
                db_client.close()
            except Exception as db_cleanup_error:
                print(f"⚠️  关闭数据库连接时发生错误: {db_cleanup_error}")

if __name__ == "__main__":
    asyncio.run(main())

