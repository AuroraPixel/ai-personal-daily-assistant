#!/usr/bin/env python3
"""
会话管理和聊天记录功能示例用法

演示如何使用ConversationService和ChatMessageService
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from service.services.conversation_service import ConversationService
from service.services.chat_message_service import ChatMessageService
from service.models.chat_message import ChatMessage
from core.database_core import DatabaseClient
from service.test_cleanup import cleanup_test_data


def test_conversation_service():
    """测试会话管理服务"""
    print("=== 测试会话管理服务 ===")
    
    conversation_service = ConversationService()
    
    # 创建新会话（自动生成UUID）
    conversation = conversation_service.create_conversation(
        user_id=1,
        title="AI助手对话",
        description="与AI助手的日常对话"
    )
    
    if conversation:
        print(f"会话创建成功: {conversation.id} - {conversation.title}")
        print(f"会话UUID（自动生成）: {conversation.id_str}")
        
        # 通过UUID获取会话
        conv_by_uuid = conversation_service.get_conversation_by_id_str(conversation.id_str)
        if conv_by_uuid:
            print(f"通过UUID获取会话成功: {conv_by_uuid.title}")
        
        # 创建会话使用自定义UUID
        custom_uuid = "my-custom-uuid-12345"
        custom_conversation = conversation_service.create_conversation(
            user_id=1,
            title="自定义UUID会话",
            description="使用自定义UUID创建的会话",
            id_str=custom_uuid
        )
        
        if custom_conversation:
            print(f"自定义UUID会话创建成功: {custom_conversation.title}")
            print(f"自定义UUID: {custom_conversation.id_str}")
            
            # 验证可以通过自定义UUID访问会话
            custom_conv_by_uuid = conversation_service.get_conversation_by_id_str(custom_uuid)
            if custom_conv_by_uuid:
                print(f"通过自定义UUID获取会话成功: {custom_conv_by_uuid.title}")
        
        # 更新会话（使用整数ID）
        updated_conversation = conversation_service.update_conversation(
            conversation.id,
            title="更新后的AI助手对话",
            description="更新后的会话描述"
        )
        
        if updated_conversation:
            print(f"会话更新成功: {updated_conversation.title}")
        
        # 通过UUID更新会话
        updated_conv_by_uuid = conversation_service.update_conversation_by_id_str(
            conversation.id_str,
            title="通过UUID更新的标题"
        )
        
        if updated_conv_by_uuid:
            print(f"通过UUID更新会话成功: {updated_conv_by_uuid.title}")
        
        # 获取会话摘要
        summary = conversation_service.get_conversation_summary(conversation.id)
        print(f"会话摘要: {summary}")
        
        # 通过UUID获取会话摘要
        summary_by_uuid = conversation_service.get_conversation_summary_by_id_str(conversation.id_str)
        print(f"通过UUID获取会话摘要: {summary_by_uuid}")
        
        # 创建更多会话
        conversations = []
        for i in range(3):
            conv = conversation_service.create_conversation(
                user_id=1,
                title=f"测试会话 {i+1}",
                description=f"这是第{i+1}个测试会话"
            )
            if conv:
                conversations.append(conv)
                print(f"创建会话: {conv.title} (UUID: {conv.id_str})")
        
        # 获取用户的所有会话
        user_conversations = conversation_service.get_user_conversations(user_id=1)
        print(f"用户会话数量: {len(user_conversations)}")
        
        # 通过UUID归档一个会话
        if conversations:
            success = conversation_service.archive_conversation_by_id_str(conversations[0].id_str)
            if success:
                print(f"通过UUID归档会话 '{conversations[0].title}' 成功")
        
        # 获取活跃会话
        active_conversations = conversation_service.get_active_conversations(user_id=1)
        print(f"活跃会话数量: {len(active_conversations)}")
        
        # 搜索会话
        search_results = conversation_service.search_conversations(1, "AI助手")
        print(f"搜索结果: {len(search_results)} 个会话")
        
        # 获取统计信息
        stats = conversation_service.get_conversation_statistics(user_id=1)
        print(f"会话统计: {stats}")
        
        return conversation
    
    else:
        print("会话创建失败")
        return None


def test_chat_message_service():
    """测试聊天记录服务"""
    print("\n=== 测试聊天记录服务 ===")
    
    conversation_service = ConversationService()
    chat_service = ChatMessageService()
    
    # 创建测试会话
    conversation = conversation_service.create_conversation(
        user_id=1,
        title="聊天测试会话",
        description="用于测试聊天记录功能"
    )
    
    if not conversation:
        print("无法创建测试会话")
        return
    
    print(f"创建会话成功: {conversation.title} (UUID: {conversation.id_str})")
    
    # 使用整数ID发送消息
    human_message = chat_service.create_message(
        conversation_id=conversation.id,
        sender_type=ChatMessage.SENDER_TYPE_HUMAN,
        content="你好，我想了解今天的天气情况",
        sender_id="user_001"
    )
    
    if human_message:
        print(f"人类消息发送成功: {human_message.content}")
    
    # 使用UUID发送AI回复
    ai_message = chat_service.create_message_by_id_str(
        conversation_id_str=conversation.id_str,
        sender_type=ChatMessage.SENDER_TYPE_AI,
        content="我来帮您查询天气信息，请稍等...",
        sender_id="ai_assistant"
    )
    
    if ai_message:
        print(f"AI消息发送成功（通过UUID）: {ai_message.content}")
    
    # 使用UUID发送工具消息
    tool_message = chat_service.create_message_by_id_str(
        conversation_id_str=conversation.id_str,
        sender_type=ChatMessage.SENDER_TYPE_TOOL,
        content="正在调用天气API获取数据...",
        sender_id="weather_tool",
        extra_data='{"tool_name": "weather_api", "status": "calling"}'
    )
    
    if tool_message:
        print(f"工具消息发送成功（通过UUID）: {tool_message.content}")
    
    # 发送AI最终回复
    if human_message:
        final_ai_message = chat_service.create_message_by_id_str(
            conversation_id_str=conversation.id_str,
            sender_type=ChatMessage.SENDER_TYPE_AI,
            content="根据天气数据，今天是晴天，温度20-25度，适合外出活动。",
            sender_id="ai_assistant",
            reply_to_id=human_message.id
        )
        
        if final_ai_message:
            print(f"AI最终回复发送成功（通过UUID）: {final_ai_message.content}")
    
    # 获取会话消息列表（使用整数ID）
    messages = chat_service.get_conversation_messages(conversation.id)
    print(f"会话消息数量: {len(messages)}")
    for message in messages:
        print(f"[{message.sender_type}] {message.content[:50]}...")
    
    # 通过UUID获取会话消息列表
    messages_by_uuid = chat_service.get_conversation_messages_by_id_str(conversation.id_str)
    print(f"通过UUID获取会话消息数量: {len(messages_by_uuid)}")
    
    # 搜索消息（使用整数ID）
    search_results = chat_service.search_messages(conversation.id, "天气")
    print(f"搜索到 {len(search_results)} 条包含'天气'的消息")
    
    # 通过UUID搜索消息
    search_results_by_uuid = chat_service.search_messages_by_id_str(conversation.id_str, "天气")
    print(f"通过UUID搜索到 {len(search_results_by_uuid)} 条包含'天气'的消息")
    
    # 获取不同类型的消息
    human_messages = chat_service.get_human_messages(conversation.id)
    ai_messages = chat_service.get_ai_messages_by_id_str(conversation.id_str)
    tool_messages = chat_service.get_tool_messages_by_id_str(conversation.id_str)
    
    print(f"人类消息: {len(human_messages)} 条")
    print(f"AI消息（通过UUID）: {len(ai_messages)} 条")
    print(f"工具消息（通过UUID）: {len(tool_messages)} 条")
    
    # 获取消息统计
    stats = chat_service.get_conversation_message_statistics(conversation.id)
    print(f"消息统计: {stats}")
    
    # 通过UUID获取消息统计
    stats_by_uuid = chat_service.get_conversation_message_statistics_by_id_str(conversation.id_str)
    print(f"通过UUID获取消息统计: {stats_by_uuid}")
    
    # 测试消息回复功能
    if human_message:
        replies = chat_service.get_message_replies(human_message.id)
        print(f"消息 '{human_message.content}' 的回复数量: {len(replies)}")
        for reply in replies:
            print(f"  回复: [{reply.sender_type}] {reply.content[:30]}...")
    
    # 标记消息为已读
    if human_message:
        success = chat_service.mark_message_as_read(human_message.id)
        if success:
            print("消息已标记为已读")


def test_integration():
    """测试会话管理和聊天记录集成"""
    print("\n=== 测试服务集成 ===")
    
    conversation_service = ConversationService()
    chat_service = ChatMessageService()
    
    user_id = 1
    
    # 创建会话
    conversation = conversation_service.create_conversation(
        user_id=user_id,
        title="集成测试会话",
        description="测试会话管理和聊天记录的集成功能"
    )
    
    if not conversation:
        print("无法创建测试会话")
        return
    
    print(f"创建会话: {conversation.title} (UUID: {conversation.id_str})")
    
    # 模拟完整的对话流程（混合使用整数ID和UUID）
    messages = [
        {"sender_type": ChatMessage.SENDER_TYPE_HUMAN, "content": "你好，我需要帮助", "sender_id": "user_001", "use_uuid": False},
        {"sender_type": ChatMessage.SENDER_TYPE_AI, "content": "你好！我很乐意帮助您。请告诉我您需要什么帮助？", "sender_id": "ai_assistant", "use_uuid": True},
        {"sender_type": ChatMessage.SENDER_TYPE_HUMAN, "content": "我想查询天气", "sender_id": "user_001", "use_uuid": True},
        {"sender_type": ChatMessage.SENDER_TYPE_AI, "content": "好的，我来帮您查询天气信息。", "sender_id": "ai_assistant", "use_uuid": False},
        {"sender_type": ChatMessage.SENDER_TYPE_TOOL, "content": "正在调用天气API...", "sender_id": "weather_tool", "use_uuid": True},
        {"sender_type": ChatMessage.SENDER_TYPE_AI, "content": "今天天气晴朗，温度22度，适合外出。", "sender_id": "ai_assistant", "use_uuid": True},
        {"sender_type": ChatMessage.SENDER_TYPE_HUMAN, "content": "谢谢！", "sender_id": "user_001", "use_uuid": False},
        {"sender_type": ChatMessage.SENDER_TYPE_AI, "content": "不客气！还有其他需要帮助的吗？", "sender_id": "ai_assistant", "use_uuid": True},
    ]
    
    # 发送所有消息
    for msg_data in messages:
        if msg_data["use_uuid"]:
            # 使用UUID发送消息
            message = chat_service.create_message_by_id_str(
                conversation_id_str=conversation.id_str,
                sender_type=msg_data["sender_type"],
                content=msg_data["content"],
                sender_id=msg_data["sender_id"]
            )
            method = "UUID"
        else:
            # 使用整数ID发送消息
            message = chat_service.create_message(
                conversation_id=conversation.id,
                sender_type=msg_data["sender_type"],
                content=msg_data["content"],
                sender_id=msg_data["sender_id"]
            )
            method = "ID"
        
        if message:
            print(f"发送消息（{method}）: [{message.sender_type}] {message.content}")
    
    # 获取会话统计
    conversation_stats = conversation_service.get_conversation_statistics(user_id)
    message_stats = chat_service.get_conversation_message_statistics_by_id_str(conversation.id_str)
    
    print(f"\n会话统计: {conversation_stats}")
    print(f"消息统计（通过UUID）: {message_stats}")
    
    # 获取最近消息
    recent_messages = chat_service.get_recent_messages_by_id_str(conversation.id_str, limit=5)
    print(f"\n最近5条消息（通过UUID）:")
    for msg in recent_messages:
        print(f"  [{msg.sender_type}] {msg.content}")
    
    # 展示UUID管理的优势
    print(f"\n=== UUID管理演示 ===")
    print(f"会话ID: {conversation.id}")
    print(f"会话UUID: {conversation.id_str}")
    print(f"通过UUID可以直接访问会话，无需知道整数ID")
    print(f"UUID在分布式系统中更容易管理和传输")


def main():
    """主函数"""
    print("🚀 会话管理和聊天记录服务使用示例（支持UUID）")
    print("=" * 60)
    
    try:
        # 初始化数据库
        db_client = DatabaseClient()
        if not db_client.initialize():
            print("数据库初始化失败")
            return
        
        # 创建数据表
        if not db_client.create_tables():
            print("创建数据表失败")
            return
        
        # 清理测试数据
        print("清理之前的测试数据...")
        cleanup_test_data()
        
        # 运行测试
        test_conversation_service()
        test_chat_message_service()
        test_integration()
        
        print("\n✅ 所有测试完成！")
        print("🎉 UUID功能已成功集成到会话管理系统中")
        
    except Exception as e:
        print(f"运行示例时发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        if 'db_client' in locals():
            db_client.close()


if __name__ == "__main__":
    """
    运行示例前，请确保：
    1. MySQL服务正在运行
    2. 数据库配置正确
    3. 已安装所有依赖
    4. JSONPlaceholder API可访问
    
    新增功能：
    - 会话和消息支持UUID管理
    - 可以通过id_str直接访问会话
    - 消息包含conversation_id_str字段
    - 支持混合使用整数ID和UUID
    """
    
    main() 