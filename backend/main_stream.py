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
from agents.items import ItemHelpers

# =========================
# 全局变量
# =========================
# 数据库客户端
db_client: Optional[DatabaseClient] = None
# 个人助手管理器
assistant_manager: Optional[PersonalAssistantManager] = None


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
        async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
            if event.type == "raw_response_event":
                print(f"Raw response event: {event.data}")
                continue
            # When the agent updates, print that
            elif event.type == "agent_updated_stream_event":
                print(f"Agent updated: {event.new_agent.name}")
                continue
            # When items are generated, print them
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    print(f"-- Tool was called {event.item.agent.name}")
                elif event.item.type == "tool_call_output_item":
                    print(f"-- Tool output: {event.item.output}")
                elif event.item.type == "message_output_item":
                    print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
                else:
                    print(f"-- Other event: {event.item.type}")
                    pass 
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

