#!/usr/bin/env python3
"""
个人助手管理器使用示例
展示如何使用 PersonalAssistantManager 类
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from core.database_core import DatabaseClient
from agent.personal_assistant_manager import PersonalAssistantManager, PersonalAssistantContext
from agents import Runner


async def main():
    """主函数 - 演示如何使用PersonalAssistantManager"""
    
    print("=" * 50)
    print("🚀 个人助手管理器使用示例")
    print("=" * 50)
    
    # 1. 初始化数据库客户端
    print("\n📁 步骤1: 初始化数据库客户端")
    db_client = DatabaseClient()
    db_client.initialize()
    db_client.create_tables()
    print("✅ 数据库客户端初始化完成")
    
    # 2. 创建个人助手管理器
    print("\n🤖 步骤2: 创建个人助手管理器")
    manager = PersonalAssistantManager(
        db_client=db_client,
        mcp_server_url="http://127.0.0.1:8002/mcp"
    )
    
    # 3. 初始化管理器
    print("\n⚙️  步骤3: 初始化管理器")
    success = await manager.initialize()
    
    if not success:
        print("❌ 管理器初始化失败，程序退出")
        return
    
    # 4. 创建用户上下文
    print("\n👤 步骤4: 创建用户上下文")
    user_id = 1
    context = manager.create_user_context(user_id)
    print(f"✅ 用户上下文创建完成: {context.user_name}")
    
    # 5. 展示可用的智能体
    print("\n🤖 步骤5: 可用的智能体")
    print(f"可用智能体: {manager.available_agents}")
    print(f"管理器状态: {manager}")
    
    # 6. 获取任务调度中心智能体
    print("\n🎯 步骤6: 获取任务调度中心智能体")
    try:
        triage_agent = manager.get_triage_agent()
        print(f"✅ 获取任务调度中心智能体: {triage_agent.name}")
        
        # 7. 使用智能体处理用户请求
        print("\n💬 步骤7: 使用智能体处理用户请求")
        
        # 示例对话
        test_messages = [
            "你好，我是新用户，请介绍一下你的功能",
            "今天天气怎么样？",
            "有什么新闻吗？",
            "推荐一个菜谱",
            "帮我记录一个待办事项：明天买菜"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- 对话 {i} ---")
            print(f"用户: {message}")
            
            try:
                # 运行智能体
                response = await Runner.run(
                    triage_agent,
                    message,
                    context=context
                )
                
                print(f"助手: 处理完成")
                
                # 显示响应摘要
                if hasattr(response, 'final_output') and response.final_output:
                    content_preview = response.final_output[:100] + "..." if len(response.final_output) > 100 else response.final_output
                    print(f"  响应: {content_preview}")
                        
            except Exception as e:
                print(f"❌ 处理消息失败: {e}")
                
    except Exception as e:
        print(f"❌ 获取智能体失败: {e}")
    
    # 8. 演示单个智能体的使用
    print("\n🔧 步骤8: 演示单个智能体的使用")
    try:
        # 获取天气智能体
        weather_agent = manager.get_weather_agent()
        print(f"✅ 获取天气智能体: {weather_agent.name}")
        
        # 获取新闻智能体
        news_agent = manager.get_news_agent()
        print(f"✅ 获取新闻智能体: {news_agent.name}")
        
        # 获取菜谱智能体
        recipe_agent = manager.get_recipe_agent()
        print(f"✅ 获取菜谱智能体: {recipe_agent.name}")
        
        # 获取个人助手智能体
        personal_agent = manager.get_personal_agent()
        print(f"✅ 获取个人助手智能体: {personal_agent.name}")
        
    except Exception as e:
        print(f"❌ 获取智能体失败: {e}")
    
    # 9. 演示上下文刷新功能
    print("\n🔄 步骤9: 演示上下文刷新功能")
    try:
        print("刷新用户偏好...")
        # 注意：refresh_user_preferences 和 refresh_user_todos 方法
        # 通常在智能体运行过程中自动调用，这里仅为演示目的
        print("  (在实际使用中，这些方法会在智能体运行时自动调用)")
        
        print("刷新用户待办事项...")
        print("  (在实际使用中，这些方法会在智能体运行时自动调用)")
        
        print("✅ 上下文刷新功能说明完成")
        
    except Exception as e:
        print(f"❌ 上下文刷新失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 个人助手管理器使用示例完成")
    print("=" * 50)


def create_simple_usage_example():
    """简单使用示例"""
    print("\n" + "=" * 30)
    print("💡 简单使用示例")
    print("=" * 30)
    
    example_code = '''
# 简单使用示例
import asyncio
from core.database_core import DatabaseClient
from agent.personal_assistant_manager import PersonalAssistantManager

async def simple_example():
    # 1. 初始化数据库
    db_client = DatabaseClient()
    db_client.initialize()
    db_client.create_tables()
    
    # 2. 创建管理器
    manager = PersonalAssistantManager(db_client)
    
    # 3. 初始化管理器
    await manager.initialize()
    
    # 4. 创建用户上下文
    context = manager.create_user_context(user_id=1)
    
    # 5. 获取智能体
    agent = manager.get_triage_agent()
    
    # 6. 使用智能体
    from agents import Runner
    response = await Runner.run(agent, "你好", context=context)
    
    print(f"助手回复: {response.final_output}")

# 运行示例
asyncio.run(simple_example())
'''
    
    print(example_code)


if __name__ == "__main__":
    try:
        # 运行主示例
        asyncio.run(main())
        
        # 显示简单使用示例
        create_simple_usage_example()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  程序被用户中断")
    except Exception as e:
        print(f"\n\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc() 