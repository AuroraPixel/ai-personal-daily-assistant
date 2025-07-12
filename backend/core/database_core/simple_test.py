#!/usr/bin/env python3
"""
简单的数据验证测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import Column, String, Integer, Text, Boolean
from core.database_core import DatabaseClient, BaseModel


# 测试模型
class SimpleUser(BaseModel):
    __tablename__ = 'simple_users'
    
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    email = Column(String(100), unique=True, nullable=False, comment='邮箱')
    password_hash = Column(String(128), nullable=False, comment='密码哈希')
    is_active = Column(Boolean, default=True, comment='是否激活')
    profile = Column(Text, comment='用户简介')


def test_validation():
    """测试数据验证功能"""
    print("=== 简单数据验证测试 ===")
    
    try:
        db_client = DatabaseClient()
        if not db_client.initialize():
            print("❌ 数据库初始化失败")
            return False
        
        # 测试有效数据
        valid_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password_hash": "hashed_password"
        }
        
        print("测试有效数据...")
        is_valid, errors = db_client.validate_model_data(SimpleUser, valid_data)
        if is_valid:
            print("✅ 有效数据验证通过")
        else:
            print(f"❌ 有效数据验证失败: {errors}")
        
        # 测试无效数据
        invalid_data = {
            "username": "test_user_invalid"
            # 缺少必需的email和password_hash字段
        }
        
        print("测试无效数据...")
        is_valid, errors = db_client.validate_model_data(SimpleUser, invalid_data)
        if not is_valid:
            print(f"✅ 无效数据验证正确失败: {errors}")
        else:
            print("❌ 无效数据验证应该失败但没有失败")
        
        db_client.close()
        return True
        
    except Exception as e:
        print(f"❌ 验证测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 简单数据验证测试")
    print("=" * 30)
    
    success = test_validation()
    
    if success:
        print("\n✅ 测试完成")
    else:
        print("\n❌ 测试失败") 