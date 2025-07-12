#!/usr/bin/env python3
"""
MySQL数据库组件测试脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import Column, String, Integer, Text, Boolean
from core.database_core import DatabaseClient, BaseModel, DatabaseConfig


# 测试模型
class TestUser(BaseModel):
    __tablename__ = 'test_users'
    
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    email = Column(String(100), unique=True, nullable=False, comment='邮箱')
    password_hash = Column(String(128), nullable=False, comment='密码哈希')
    is_active = Column(Boolean, default=True, comment='是否激活')
    profile = Column(Text, comment='用户简介')


def test_database_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    
    try:
        db_client = DatabaseClient()
        if db_client.initialize():
            print("✅ 数据库连接成功")
            
            # 获取数据库信息
            db_info = db_client.get_database_info()
            if db_info:
                print(f"📊 数据库信息: {db_info}")
            
            db_client.close()
            return True
        else:
            print("❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"❌ 连接测试异常: {e}")
        return False


def test_table_operations():
    """测试表操作"""
    print("\n=== 测试表操作 ===")
    
    try:
        with DatabaseClient() as db_client:
            # 创建表
            if db_client.create_tables():
                print("✅ 测试表创建成功")
            
            # 获取表信息
            table_info = db_client.get_table_info('test_users')
            if table_info:
                print(f"📋 表信息: {table_info['name']}")
                print(f"   - 列数: {len(table_info['columns'])}")
            
            # 获取表行数
            row_count = db_client.get_table_row_count('test_users')
            print(f"📊 表行数: {row_count}")
            
            return True
    except Exception as e:
        print(f"❌ 表操作异常: {e}")
        return False


def test_crud_operations():
    """测试CRUD操作"""
    print("\n=== 测试CRUD操作 ===")
    
    try:
        with DatabaseClient() as db_client:
            with db_client.get_session() as session:
                # 创建用户
                user = TestUser(
                    username="test_user",
                    email="test@example.com",
                    password_hash="hashed_password",
                    profile="这是一个测试用户"
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"✅ 创建用户: {user.id} - {user.username}")
                
                # 查询用户
                found_user = session.query(TestUser).filter(
                    TestUser.username == "test_user"
                ).first()
                if found_user:
                    print(f"✅ 查询用户: {found_user.username}")
                
                # 更新用户
                found_user.profile = "更新后的用户简介"
                session.commit()
                print(f"✅ 更新用户: {found_user.profile}")
                
                # 删除用户
                session.delete(found_user)
                session.commit()
                print("✅ 删除用户成功")
                
                return True
    except Exception as e:
        print(f"❌ CRUD操作异常: {e}")
        return False


def test_model_manager():
    """测试模型管理器"""
    print("\n=== 测试模型管理器 ===")
    
    try:
        with DatabaseClient() as db_client:
            manager = db_client.get_model_manager(TestUser)
            
            with db_client.get_session() as session:
                # 创建用户
                user = manager.create(
                    session,
                    username="manager_user",
                    email="manager@example.com",
                    password_hash="hashed_password",
                    profile="通过管理器创建的用户"
                )
                print(f"✅ 管理器创建用户: {user.id} - {user.username}")
                
                # 查询用户
                found_user = manager.get_by_id(session, user.id)
                if found_user:
                    print(f"✅ 管理器查询用户: {found_user.username}")
                
                # 更新用户
                updated_user = manager.update(
                    session,
                    user.id,
                    profile="管理器更新后的简介"
                )
                if updated_user:
                    print(f"✅ 管理器更新用户: {updated_user.profile}")
                
                # 获取所有用户
                all_users = manager.get_all(session, limit=10)
                print(f"✅ 管理器获取所有用户: {len(all_users)} 个")
                
                # 删除用户
                if manager.delete(session, user.id):
                    print("✅ 管理器删除用户成功")
                
                return True
    except Exception as e:
        print(f"❌ 模型管理器异常: {e}")
        return False


def test_batch_operations():
    """测试批量操作"""
    print("\n=== 测试批量操作 ===")
    
    try:
        with DatabaseClient() as db_client:
            # 准备测试数据
            test_data = [
                {
                    "username": f"batch_user_{i}",
                    "email": f"batch_user_{i}@example.com",
                    "password_hash": f"hash_{i}",
                    "profile": f"批量用户 {i}"
                }
                for i in range(10)
            ]
            
            # 批量插入
            if db_client.batch_insert(TestUser, test_data, batch_size=5):
                print("✅ 批量插入成功")
            
            # 检查行数
            row_count = db_client.get_table_row_count('test_users')
            print(f"📊 插入后表行数: {row_count}")
            
            # 清空表
            if db_client.truncate_table('test_users'):
                print("✅ 清空表成功")
            
            return True
    except Exception as e:
        print(f"❌ 批量操作异常: {e}")
        return False


def test_raw_sql():
    """测试原生SQL"""
    print("\n=== 测试原生SQL ===")
    
    try:
        with DatabaseClient() as db_client:
            # 插入测试数据
            with db_client.get_session() as session:
                user = TestUser(
                    username="sql_test_user",
                    email="sql@example.com",
                    password_hash="sql_hash"
                )
                session.add(user)
                session.commit()
            
            # 执行原生SQL查询
            result = db_client.execute_query(
                "SELECT id, username, email FROM test_users WHERE username = :username",
                {"username": "sql_test_user"}
            )
            
            if result:
                print(f"✅ 原生SQL查询成功: {len(result)} 条记录")
                for row in result:
                    print(f"   - {row['id']}: {row['username']} - {row['email']}")
            
            return True
    except Exception as e:
        print(f"❌ 原生SQL异常: {e}")
        return False


def test_data_validation():
    """测试数据验证"""
    print("\n=== 测试数据验证 ===")
    
    try:
        with DatabaseClient() as db_client:
            # 测试有效数据
            valid_data = {
                "username": "valid_user",
                "email": "valid@example.com",
                "password_hash": "valid_hash"
            }
            
            is_valid, errors = db_client.validate_model_data(TestUser, valid_data)
            if is_valid:
                print("✅ 有效数据验证通过")
            else:
                print(f"❌ 有效数据验证失败: {errors}")
            
            # 测试无效数据
            invalid_data = {
                "username": "invalid_user",
                # 缺少必需字段
            }
            
            is_valid, errors = db_client.validate_model_data(TestUser, invalid_data)
            if not is_valid:
                print(f"✅ 无效数据验证正确失败: {errors}")
            else:
                print("❌ 无效数据验证应该失败")
            
            return True
    except Exception as e:
        print(f"❌ 数据验证异常: {e}")
        return False


def test_utility_functions():
    """测试工具函数"""
    print("\n=== 测试工具函数 ===")
    
    try:
        with DatabaseClient() as db_client:
            # 备份表（需要先有数据）
            with db_client.get_session() as session:
                user = TestUser(
                    username="backup_user",
                    email="backup@example.com",
                    password_hash="backup_hash"
                )
                session.add(user)
                session.commit()
            
            # 备份表
            backup_name = "test_users_backup"
            if db_client.backup_table('test_users', backup_name):
                print(f"✅ 表备份成功: {backup_name}")
            
            # 获取备份表行数
            backup_count = db_client.get_table_row_count(backup_name)
            print(f"📊 备份表行数: {backup_count}")
            
            return True
    except Exception as e:
        print(f"❌ 工具函数异常: {e}")
        return False


def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    try:
        with DatabaseClient() as db_client:
            # 删除测试表
            if db_client.truncate_table('test_users'):
                print("✅ 清空测试表成功")
            
            # 删除备份表
            try:
                db_client.execute_query("DROP TABLE IF EXISTS test_users_backup")
                print("✅ 删除备份表成功")
            except:
                pass
            
            return True
    except Exception as e:
        print(f"❌ 清理异常: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 MySQL数据库组件测试")
    print("=" * 50)
    
    tests = [
        ("数据库连接", test_database_connection),
        ("表操作", test_table_operations),
        ("CRUD操作", test_crud_operations),
        ("模型管理器", test_model_manager),
        ("批量操作", test_batch_operations),
        ("原生SQL", test_raw_sql),
        ("数据验证", test_data_validation),
        ("工具函数", test_utility_functions),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n🔍 运行测试: {name}")
            if test_func():
                print(f"✅ 测试通过: {name}")
                passed += 1
            else:
                print(f"❌ 测试失败: {name}")
                failed += 1
        except Exception as e:
            print(f"💥 测试异常: {name} - {e}")
            failed += 1
    
    # 清理测试数据
    cleanup_test_data()
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！MySQL组件工作正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查配置和连接。")
        return False


if __name__ == "__main__":
    """
    运行测试前，请确保：
    1. MySQL服务正在运行
    2. 数据库配置正确
    3. 用户有足够的权限
    4. 已安装所有依赖
    """
    
    try:
        success = main()
        if success:
            print("\n✅ 测试完成！")
            sys.exit(0)
        else:
            print("\n❌ 测试失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生未知错误: {e}")
        sys.exit(1) 