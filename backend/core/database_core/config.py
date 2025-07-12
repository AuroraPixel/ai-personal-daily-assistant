"""
数据库配置管理
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    """数据库配置管理类"""
    
    def __init__(self):
        """初始化数据库配置"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.username = os.getenv('DB_USERNAME', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_DATABASE', 'personal_assistant')
        self.charset = os.getenv('DB_CHARSET', 'utf8mb4')
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '10'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.getenv('DB_POOL_RECYCLE', '3600'))
        self.echo = os.getenv('DB_ECHO', 'false').lower() == 'true'
    
    def get_connection_url(self) -> str:
        """
        获取数据库连接URL
        
        Returns:
            数据库连接URL字符串
        """
        return (
            f"mysql+pymysql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
            f"?charset={self.charset}"
        )
    
    def get_engine_kwargs(self) -> dict:
        """
        获取数据库引擎配置参数
        
        Returns:
            引擎配置参数字典
        """
        return {
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle,
            'echo': self.echo,
            'pool_pre_ping': True,  # 连接前检查可用性
            'connect_args': {
                'charset': self.charset,
                'autocommit': False,
            }
        }
    
    def validate(self) -> bool:
        """
        验证数据库配置是否完整
        
        Returns:
            配置是否有效
        """
        required_fields = [self.host, self.username, self.database]
        return all(field for field in required_fields)
    
    def __str__(self) -> str:
        """配置信息字符串表示（隐藏密码）"""
        return (
            f"DatabaseConfig(host={self.host}, port={self.port}, "
            f"username={self.username}, database={self.database})"
        ) 