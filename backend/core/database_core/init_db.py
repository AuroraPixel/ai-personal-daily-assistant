#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database_core import DatabaseClient, DatabaseConfig
from core.database_core.utils import DatabaseUtils


def check_mysql_connection():
    """检查MySQL连接"""
    print("=== 检查MySQL连接 ===")
    
    try:
        db_client = DatabaseClient()
        if db_client.initialize():
            print("✅ MySQL连接成功")
            
            # 获取数据库信息
            db_info = db_client.get_database_info()
            if db_info:
                print(f"📊 数据库信息:")
                print(f"   - 引擎: {db_info.get('engine_name', 'unknown')}")
                print(f"   - 表数量: {db_info.get('table_count', 0)}")
                print(f"   - 连接URL: {db_info.get('url', 'unknown')}")
            
            db_client.close()
            return True
        else:
            print("❌ MySQL连接失败")
            return False
    except Exception as e:
        print(f"❌ MySQL连接异常: {e}")
        return False


def create_database_tables():
    """创建数据库表"""
    print("\n=== 创建数据库表 ===")
    
    try:
        db_client = DatabaseClient()
        if not db_client.initialize():
            print("❌ 数据库初始化失败")
            return False
        
        # 创建表
        if db_client.create_tables():
            print("✅ 数据库表创建成功")
            
            # 获取表信息
            db_info = db_client.get_database_info()
            if db_info and db_info.get('tables'):
                print(f"📋 已创建的表:")
                for table in db_info['tables']:
                    print(f"   - {table}")
            
            db_client.close()
            return True
        else:
            print("❌ 数据库表创建失败")
            db_client.close()
            return False
            
    except Exception as e:
        print(f"❌ 创建表时发生异常: {e}")
        return False


def show_configuration():
    """显示数据库配置"""
    print("\n=== 数据库配置 ===")
    
    try:
        config = DatabaseConfig()
        print(f"🔧 配置信息:")
        print(f"   - 主机: {config.host}")
        print(f"   - 端口: {config.port}")
        print(f"   - 用户名: {config.username}")
        print(f"   - 数据库: {config.database}")
        print(f"   - 字符集: {config.charset}")
        print(f"   - 连接池大小: {config.pool_size}")
        print(f"   - 最大溢出: {config.max_overflow}")
        print(f"   - 连接超时: {config.pool_timeout}")
        print(f"   - 连接回收: {config.pool_recycle}")
        print(f"   - 启用回显: {config.echo}")
        
        if config.validate():
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
            
    except Exception as e:
        print(f"❌ 配置检查异常: {e}")


def main():
    """主函数"""
    print("🚀 MySQL数据库组件初始化")
    print("=" * 50)
    
    # 显示配置
    show_configuration()
    
    # 检查连接
    if not check_mysql_connection():
        print("\n❌ 初始化失败：无法连接到MySQL数据库")
        print("请检查以下项目：")
        print("1. MySQL服务是否正在运行")
        print("2. 数据库配置是否正确")
        print("3. 用户权限是否足够")
        print("4. 环境变量是否设置正确")
        return False
    
    # 创建表
    if not create_database_tables():
        print("\n❌ 初始化失败：无法创建数据库表")
        return False
    
    print("\n🎉 数据库初始化完成！")
    print("现在您可以使用MySQL组件进行数据库操作了。")
    
    return True


if __name__ == "__main__":
    """
    运行此脚本前，请确保：
    1. 已安装依赖：pip install -r requirements.txt
    2. 已配置环境变量或创建.env文件
    3. MySQL服务正在运行
    4. 数据库用户有足够的权限
    """
    
    try:
        success = main()
        if success:
            print("\n✅ 初始化成功！")
            sys.exit(0)
        else:
            print("\n❌ 初始化失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  初始化被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 初始化过程中发生未知错误: {e}")
        sys.exit(1) 