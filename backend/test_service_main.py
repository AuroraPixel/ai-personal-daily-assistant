#!/usr/bin/env python3
"""
测试服务主要功能
测试 get_user_notes 业务逻辑

Author: Andrew Wang
"""

import sys
import os
import json
from datetime import datetime

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# 导入服务管理器
from service.service_manager import service_manager

# 导入服务
from service.services.note_service import NoteService
from service.services.user_service import UserService

# 导入数据库和向量数据库
from core.database_core import DatabaseClient
from core.vector_core import ChromaVectorClient, VectorConfig


def init_test_environment():
    """初始化测试环境"""
    print("🔄 正在初始化测试环境...")
    
    # 使用服务管理器初始化
    if not service_manager.initialize():
        print("❌ 服务管理器初始化失败")
        return False
    
    print("✅ 服务管理器初始化成功")
    return True


def test_create_sample_notes(note_service: NoteService, user_id: int):
    """创建测试用的笔记数据"""
    print(f"📝 为用户 {user_id} 创建测试笔记...")
    
    sample_notes = [
        {
            "title": "每日学习计划",
            "content": "今天要学习Python编程和数据库设计，重点关注SQLAlchemy的使用。",
            "tag": "lifestyle tips",
            "status": "published"
        },
        {
            "title": "健康饮食建议",
            "content": "多吃蔬菜水果，少吃油腻食物。每天喝8杯水，保持身体健康。",
            "tag": "cooking advice",
            "status": "draft"
        },
        {
            "title": "今日天气预报",
            "content": "今天多云转晴，温度15-25度，适合户外活动。记得带上外套防风。",
            "tag": "weather interpretation",
            "status": "published"
        },
        {
            "title": "科技新闻摘要",
            "content": "最新的AI技术发展动态，包括GPT模型的改进和自动驾驶汽车的进展。",
            "tag": "news context",
            "status": "published"
        },
        {
            "title": "工作备忘录",
            "content": "下周需要完成项目文档，准备客户演示，安排团队会议。",
            "tag": "",
            "status": "draft"
        }
    ]
    
    created_notes = []
    for note_data in sample_notes:
        note = note_service.create_note(
            user_id=user_id,
            title=note_data["title"],
            content=note_data["content"],
            tag=note_data["tag"] if note_data["tag"] else None,
            status=note_data["status"]
        )
        if note:
            created_notes.append(note)
            print(f"  ✅ 创建笔记: {note.title}")
        else:
            print(f"  ❌ 创建笔记失败: {note_data['title']}")
    
    print(f"📝 成功创建 {len(created_notes)} 条笔记")
    return created_notes


def test_get_user_notes_basic(note_service: NoteService, user_id: int):
    """测试基本的获取用户笔记功能"""
    print(f"\n🔍 测试获取用户 {user_id} 的所有笔记...")
    
    # 获取所有笔记
    notes = note_service.get_user_notes(user_id)
    print(f"📊 找到 {len(notes)} 条笔记")
    
    for note in notes:
        print(f"  📄 笔记ID: {note.id}, 标题: {note.title}, 状态: {note.status}, 标签: {note.tag}")
    
    return notes


def test_get_user_notes_with_filters(note_service: NoteService, user_id: int):
    """测试带过滤条件的获取用户笔记功能"""
    print(f"\n🔍 测试带过滤条件的获取用户 {user_id} 笔记...")
    
    # 测试按状态过滤
    print("  📋 按状态过滤 - 只获取已发布的笔记:")
    published_notes = note_service.get_user_notes(user_id, status='published')
    print(f"    📊 找到 {len(published_notes)} 条已发布笔记")
    for note in published_notes:
        print(f"      📄 {note.title} (状态: {note.status})")
    
    # 测试按标签过滤
    print("  📋 按标签过滤 - 只获取 'lifestyle tips' 标签的笔记:")
    lifestyle_notes = note_service.get_user_notes(user_id, tag='lifestyle tips')
    print(f"    📊 找到 {len(lifestyle_notes)} 条生活建议笔记")
    for note in lifestyle_notes:
        print(f"      📄 {note.title} (标签: {note.tag})")
    
    # 测试搜索关键词
    print("  📋 搜索关键词 - 搜索包含 '学习' 的笔记:")
    search_notes = note_service.get_user_notes(user_id, search_query='学习')
    print(f"    📊 找到 {len(search_notes)} 条包含'学习'的笔记")
    for note in search_notes:
        print(f"      📄 {note.title}")
    
    # 测试分页
    print("  📋 分页测试 - 获取前2条笔记:")
    paginated_notes = note_service.get_user_notes(user_id, limit=2, offset=0)
    print(f"    📊 找到 {len(paginated_notes)} 条笔记 (限制2条)")
    for note in paginated_notes:
        print(f"      📄 {note.title}")


def test_get_user_notes_edge_cases(note_service: NoteService):
    """测试边界情况"""
    print(f"\n🔍 测试边界情况...")
    
    # 测试不存在的用户
    print("  📋 测试不存在的用户 (ID: 999):")
    notes_999 = note_service.get_user_notes(999)
    print(f"    📊 找到 {len(notes_999)} 条笔记")
    
    # 测试无效状态过滤
    print("  📋 测试无效状态过滤:")
    invalid_status_notes = note_service.get_user_notes(1, status='invalid_status')
    print(f"    📊 找到 {len(invalid_status_notes)} 条笔记")


def test_user_service_integration(user_service: UserService, user_id: int):
    """测试用户服务集成"""
    print(f"\n👤 测试用户服务集成...")
    
    # 验证用户存在
    user_exists = user_service.validate_user_exists(user_id)
    print(f"  📊 用户 {user_id} 是否存在: {user_exists}")
    
    if user_exists:
        # 获取用户信息
        user = user_service.get_user(user_id)
        if user:
            print(f"  👤 用户信息:")
            print(f"    姓名: {user.name}")
            print(f"    邮箱: {user.email}")
            print(f"    用户名: {user.username}")
            print(f"    电话: {user.phone}")


def test_note_statistics(note_service: NoteService, user_id: int):
    """测试笔记统计功能"""
    print(f"\n📊 测试用户 {user_id} 的笔记统计...")
    
    stats = note_service.get_notes_statistics(user_id)
    
    print(f"  📊 统计结果:")
    print(f"    总笔记数: {stats.get('total_notes', 0)}")
    print(f"    按状态统计: {stats.get('status_counts', {})}")
    print(f"    按标签统计: {stats.get('tag_counts', {})}")
    print(f"    总标签数: {stats.get('total_tags', 0)}")
    print(f"    所有标签: {stats.get('tags', [])}")
    
    recent_notes = stats.get('recent_notes', [])
    print(f"    最近更新的笔记 ({len(recent_notes)} 条):")
    for note_info in recent_notes:
        print(f"      📄 {note_info.get('title', 'N/A')} (标签: {note_info.get('tag', '无')})")


def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 开始测试 get_user_notes 业务逻辑")
    print("=" * 60)
    
    # 初始化测试环境
    if not init_test_environment():
        print("❌ 测试环境初始化失败，退出测试")
        return
    
    # 测试用户ID
    test_user_id = 1
    
    try:
        # 获取服务实例
        db_client = service_manager.get_db_client()
        vector_client = service_manager.get_vector_client()
        
        # 创建服务实例
        note_service = NoteService(db_client, vector_client)
        user_service = UserService()
        
        print(f"\n🎯 目标用户ID: {test_user_id}")
        
        # 测试用户服务
        test_user_service_integration(user_service, test_user_id)
        
        # 创建测试数据
        test_create_sample_notes(note_service, test_user_id)
        
        # 测试基本功能
        all_notes = test_get_user_notes_basic(note_service, test_user_id)
        
        # 测试过滤功能
        test_get_user_notes_with_filters(note_service, test_user_id)
        
        # 测试边界情况
        test_get_user_notes_edge_cases(note_service)
        
        # 测试统计功能
        test_note_statistics(note_service, test_user_id)
        
        # 输出服务管理器统计
        print(f"\n📈 服务管理器统计:")
        stats = service_manager.get_stats()
        print(f"  数据库客户端状态: {'✅ 正常' if stats['db_client_active'] else '❌ 异常'}")
        print(f"  向量数据库状态: {'✅ 正常' if stats['vector_client_active'] else '❌ 异常'}")
        print(f"  服务实例数量: {stats['services_count']}")
        print(f"  用户缓存大小: {stats['user_cache_size']}")
        print(f"  令牌缓存大小: {stats['token_cache_size']}")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理资源
        print("\n🧹 清理测试环境...")
        service_manager.close()
        print("✅ 测试环境已清理")


if __name__ == "__main__":
    main() 