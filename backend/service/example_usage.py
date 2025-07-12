#!/usr/bin/env python3
"""
Service层使用示例

演示如何使用用户服务、偏好设置、笔记、待办事项等服务
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from service.services.user_service import UserService
from service.services.preference_service import PreferenceService
from service.services.note_service import NoteService
from service.services.todo_service import TodoService
from core.database_core import DatabaseClient
from service.test_cleanup import cleanup_test_data


def test_user_service():
    """测试用户服务"""
    print("=== 测试用户服务 ===")
    
    user_service = UserService()
    
    # 获取用户信息
    user = user_service.get_user(1)
    if user:
        print(f"用户信息: {user.name} ({user.email})")
    
    # 验证用户是否存在
    exists = user_service.validate_user_exists(1)
    print(f"用户1是否存在: {exists}")
    
    # 获取用户显示名称
    display_name = user_service.get_user_display_name(1)
    print(f"用户显示名称: {display_name}")
    
    # 搜索用户
    users = user_service.search_users_by_name("Leanne")
    print(f"搜索到用户: {len(users)} 个")


def test_preference_service():
    """测试偏好设置服务"""
    print("\n=== 测试偏好设置服务 ===")
    
    preference_service = PreferenceService()
    
    # 保存用户偏好设置
    preferences = {
        "theme": "dark",
        "language": "zh-CN",
        "notifications": {
            "email": True,
            "push": False
        },
        "dashboard": {
            "show_stats": True,
            "items_per_page": 20
        }
    }
    
    success = preference_service.save_user_preferences(1, preferences)
    print(f"保存偏好设置: {'成功' if success else '失败'}")
    
    # 获取用户偏好设置
    saved_preferences = preference_service.get_user_preferences(1)
    print(f"获取偏好设置: {saved_preferences}")
    
    # 更新特定设置
    success = preference_service.set_user_preference_value(1, "theme", "light")
    print(f"更新主题设置: {'成功' if success else '失败'}")
    
    # 获取特定设置值
    theme = preference_service.get_user_preference_value(1, "theme", "default")
    print(f"当前主题: {theme}")
    
    # 获取所有偏好设置
    all_preferences = preference_service.get_all_user_preferences(1)
    print(f"所有偏好设置: {all_preferences}")


def test_note_service():
    """测试笔记服务"""
    print("\n=== 测试笔记服务 ===")
    
    note_service = NoteService()
    
    # 创建笔记
    note = note_service.create_note(
        user_id=1,
        title="我的第一篇笔记",
        content="这是笔记的内容，包含一些重要的信息。",
        tags=["工作", "重要", "项目"],
        status="draft"
    )
    
    if note:
        print(f"创建笔记成功: {note.id} - {note.title}")
        
        # 更新笔记
        updated_note = note_service.update_note(
            note.id,
            title="更新后的笔记标题",
            content="更新后的笔记内容。",
            tags=["工作", "重要", "项目", "更新"],
            status="published"
        )
        
        if updated_note:
            print(f"更新笔记成功: {updated_note.title}")
        
        # 获取笔记摘要
        summary = note_service.get_note_summary(note.id)
        print(f"笔记摘要: {summary}")
        
        # 搜索笔记
        search_results = note_service.search_notes(1, "更新")
        print(f"搜索结果: {len(search_results)} 个笔记")
        
        # 获取用户标签
        tags = note_service.get_user_tags(1)
        print(f"用户标签: {tags}")
        
        # 获取统计信息
        stats = note_service.get_notes_statistics(1)
        print(f"笔记统计: {stats}")


def test_todo_service():
    """测试待办事项服务"""
    print("\n=== 测试待办事项服务 ===")
    
    todo_service = TodoService()
    
    # 创建待办事项
    from datetime import datetime, timedelta
    due_date = datetime.now() + timedelta(days=7)
    
    todo = todo_service.create_todo(
        user_id=1,
        title="完成项目文档",
        description="编写项目的技术文档和用户手册",
        priority="high",
        due_date=due_date
    )
    
    if todo:
        print(f"创建待办事项成功: {todo.id} - {todo.title}")
        
        # 获取待办事项摘要
        summary = todo_service.get_todo_summary(todo.id)
        print(f"待办事项摘要: {summary}")
        
        # 创建关联笔记的待办事项
        note_service = NoteService()
        note = note_service.create_note(
            user_id=1,
            title="项目文档笔记",
            content="记录项目文档的要点和结构"
        )
        
        if note:
            todo_with_note = todo_service.create_todo(
                user_id=1,
                title="审查项目文档",
                description="审查和完善项目文档",
                priority="medium",
                note_id=note.id
            )
            
            if todo_with_note:
                print(f"创建关联笔记的待办事项成功: {todo_with_note.id}")
        
        # 获取用户待办事项
        todos = todo_service.get_user_todos(1)
        print(f"用户待办事项: {len(todos)} 个")
        
        # 完成待办事项
        success = todo_service.complete_todo(todo.id)
        print(f"完成待办事项: {'成功' if success else '失败'}")
        
        # 搜索待办事项
        search_results = todo_service.search_todos(1, "项目")
        print(f"搜索结果: {len(search_results)} 个待办事项")
        
        # 获取统计信息
        stats = todo_service.get_todos_statistics(1)
        print(f"待办事项统计: {stats}")


def test_integration():
    """测试服务集成"""
    print("\n=== 测试服务集成 ===")
    
    # 创建服务实例
    user_service = UserService()
    preference_service = PreferenceService()
    note_service = NoteService()
    todo_service = TodoService()
    
    user_id = 1
    
    # 获取用户信息
    user = user_service.get_user(user_id)
    if not user:
        print(f"用户 {user_id} 不存在")
        return
    
    print(f"用户: {user.name} ({user.email})")
    
    # 设置用户偏好
    preferences = {
        "workspace": {
            "default_note_status": "draft",
            "default_todo_priority": "medium",
            "auto_save": True
        }
    }
    
    preference_service.save_user_preferences(user_id, preferences, "workspace")
    
    # 创建笔记
    note = note_service.create_note(
        user_id=user_id,
        title="工作计划",
        content="本周的工作计划和目标",
        tags=["工作", "计划"]
    )
    
    if note:
        print(f"创建笔记: {note.title}")
        
        # 创建关联的待办事项
        todo = todo_service.create_todo(
            user_id=user_id,
            title="完成工作计划",
            description="按照笔记中的计划完成工作",
            priority="high",
            note_id=note.id
        )
        
        if todo:
            print(f"创建关联待办事项: {todo.title}")
    
    # 获取用户数据概览
    print("\n用户数据概览:")
    print(f"- 偏好设置类别: {len(preference_service.get_preference_categories(user_id))}")
    print(f"- 笔记统计: {note_service.get_notes_statistics(user_id)}")
    print(f"- 待办事项统计: {todo_service.get_todos_statistics(user_id)}")


def main():
    """主函数"""
    print("🚀 Service层使用示例")
    print("=" * 50)
    
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
        test_user_service()
        test_preference_service()
        test_note_service()
        test_todo_service()
        test_integration()
        
        print("\n✅ 所有测试完成！")
        
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
    """
    
    main() 