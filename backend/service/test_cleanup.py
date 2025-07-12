#!/usr/bin/env python
"""
测试数据清理脚本

用于清理测试过程中产生的数据，确保测试之间的数据隔离
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database_core import DatabaseClient
from service.services.user_service import UserService
from service.models.user_preference import UserPreference
from service.models.note import Note
from service.models.todo import Todo


def cleanup_test_data():
    """清理测试数据"""
    print("开始清理测试数据...")
    
    try:
        # 初始化数据库客户端
        db_client = DatabaseClient()
        db_client.initialize()
        
        # 获取所有测试用户ID（JSONPlaceholder API的前5个用户）
        user_service = UserService()
        test_user_ids = []
        for i in range(1, 6):  # 用户ID 1-5
            if user_service.validate_user_exists(i):
                test_user_ids.append(i)
        
        print(f"发现测试用户: {test_user_ids}")
        
        with db_client.get_session() as session:
            # 1. 清理待办事项
            todo_count = session.query(Todo).filter(Todo.user_id.in_(test_user_ids)).count()
            if todo_count > 0:
                session.query(Todo).filter(Todo.user_id.in_(test_user_ids)).delete()
                print(f"已清理 {todo_count} 个待办事项")
            
            # 2. 清理笔记
            note_count = session.query(Note).filter(Note.user_id.in_(test_user_ids)).count()
            if note_count > 0:
                session.query(Note).filter(Note.user_id.in_(test_user_ids)).delete()
                print(f"已清理 {note_count} 个笔记")
            
            # 3. 清理用户偏好设置
            pref_count = session.query(UserPreference).filter(UserPreference.user_id.in_(test_user_ids)).count()
            if pref_count > 0:
                session.query(UserPreference).filter(UserPreference.user_id.in_(test_user_ids)).delete()
                print(f"已清理 {pref_count} 个偏好设置")
            
            # 提交更改
            session.commit()
            print("测试数据清理完成！")
            
    except Exception as e:
        print(f"清理测试数据失败: {e}")
        return False
    
    finally:
        if 'db_client' in locals():
            db_client.close()
    
    return True


def reset_test_environment():
    """重置测试环境"""
    print("重置测试环境...")
    
    # 首先清理数据
    if not cleanup_test_data():
        print("清理测试数据失败，无法重置环境")
        return False
    
    # 可以在这里添加其他重置操作
    print("测试环境重置完成！")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='测试数据清理工具')
    parser.add_argument('--reset', action='store_true', help='重置整个测试环境')
    parser.add_argument('--cleanup', action='store_true', help='仅清理测试数据')
    
    args = parser.parse_args()
    
    if args.reset:
        success = reset_test_environment()
    elif args.cleanup:
        success = cleanup_test_data()
    else:
        print("请指定操作: --cleanup 或 --reset")
        success = False
    
    sys.exit(0 if success else 1) 