"""
数据库客户端实现
"""

import logging
from typing import Optional, Dict, Any, List, Type, Union
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .config import DatabaseConfig
from .models import BaseModel, ModelManager
from .utils import DatabaseUtils

logger = logging.getLogger(__name__)


class DatabaseClient:
    """
    数据库客户端类
    提供数据库连接和操作的主要接口
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        初始化数据库客户端
        
        Args:
            config: 数据库配置，默认使用环境变量配置
        """
        self.config = config or DatabaseConfig()
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        初始化数据库连接
        
        Returns:
            初始化是否成功
        """
        if self._initialized:
            logger.warning("数据库客户端已经初始化")
            return True
        
        try:
            # 验证配置
            if not self.config.validate():
                logger.error("数据库配置验证失败")
                return False
            
            # 创建引擎
            connection_url = self.config.get_connection_url()
            engine_kwargs = self.config.get_engine_kwargs()
            
            self.engine = create_engine(connection_url, **engine_kwargs)
            
            # 测试连接
            if not DatabaseUtils.test_connection(self.engine):
                logger.error("数据库连接测试失败")
                return False
            
            # 创建会话工厂
            self.session_factory = sessionmaker(bind=self.engine)
            
            self._initialized = True
            logger.info("数据库客户端初始化成功")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"数据库初始化失败: {e}")
            return False
    
    def create_tables(self) -> bool:
        """
        创建数据表
        
        Returns:
            创建是否成功
        """
        if not self._initialized:
            logger.error("数据库客户端未初始化")
            return False
        
        try:
            BaseModel.metadata.create_all(self.engine)
            logger.info("数据表创建成功")
            return True
        except SQLAlchemyError as e:
            logger.error(f"数据表创建失败: {e}")
            return False
    
    def drop_tables(self) -> bool:
        """
        删除数据表
        
        Returns:
            删除是否成功
        """
        if not self._initialized:
            logger.error("数据库客户端未初始化")
            return False
        
        try:
            BaseModel.metadata.drop_all(self.engine)
            logger.info("数据表删除成功")
            return True
        except SQLAlchemyError as e:
            logger.error(f"数据表删除失败: {e}")
            return False
    
    @contextmanager
    def get_session(self) -> Session:
        """
        获取数据库会话的上下文管理器
        
        Returns:
            数据库会话
        """
        if not self._initialized:
            raise RuntimeError("数据库客户端未初始化")
        
        session = self.session_factory()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"会话操作失败，已回滚: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, sql: str, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        执行查询SQL
        
        Args:
            sql: SQL语句
            params: 参数字典
            
        Returns:
            查询结果列表或None
        """
        if not self._initialized:
            logger.error("数据库客户端未初始化")
            return None
        
        return DatabaseUtils.execute_raw_sql(self.engine, sql, params)
    
    def get_model_manager(self, model_class: Type[BaseModel]) -> ModelManager:
        """
        获取模型管理器
        
        Args:
            model_class: 模型类
            
        Returns:
            模型管理器实例
        """
        return ModelManager(model_class)
    
    def get_database_info(self) -> Optional[Dict[str, Any]]:
        """
        获取数据库信息
        
        Returns:
            数据库信息字典或None
        """
        if not self._initialized:
            logger.error("数据库客户端未初始化")
            return None
        
        return DatabaseUtils.get_database_info(self.engine)
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        获取数据表信息
        
        Args:
            table_name: 表名
            
        Returns:
            表信息字典或None
        """
        if not self._initialized:
            logger.error("数据库客户端未初始化")
            return None
        
        return DatabaseUtils.get_table_info(self.engine, table_name)
    
    def backup_table(self, table_name: str, backup_table_name: str) -> bool:
        """
        备份数据表
        
        Args:
            table_name: 源表名
            backup_table_name: 备份表名
            
        Returns:
            备份是否成功
        """
        if not self._initialized:
            logger.error("数据库客户端未初始化")
            return False
        
        return DatabaseUtils.backup_table(self.engine, table_name, backup_table_name)
    
    def truncate_table(self, table_name: str) -> bool:
        """
        清空数据表
        
        Args:
            table_name: 表名
            
        Returns:
            清空是否成功
        """
        if not self._initialized:
            logger.error("数据库客户端未初始化")
            return False
        
        return DatabaseUtils.truncate_table(self.engine, table_name)
    
    def get_table_row_count(self, table_name: str) -> Optional[int]:
        """
        获取表的行数
        
        Args:
            table_name: 表名
            
        Returns:
            行数或None
        """
        if not self._initialized:
            logger.error("数据库客户端未初始化")
            return None
        
        return DatabaseUtils.get_table_row_count(self.engine, table_name)
    
    def batch_insert(self, model_class: Type[BaseModel], data_list: List[Dict], 
                    batch_size: int = 1000) -> bool:
        """
        批量插入数据
        
        Args:
            model_class: 模型类
            data_list: 数据列表
            batch_size: 批次大小
            
        Returns:
            插入是否成功
        """
        if not self._initialized:
            logger.error("数据库客户端未初始化")
            return False
        
        with self.get_session() as session:
            return DatabaseUtils.batch_insert(session, model_class, data_list, batch_size)
    
    def validate_model_data(self, model_class: Type[BaseModel], 
                           data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证模型数据
        
        Args:
            model_class: 模型类
            data: 数据字典
            
        Returns:
            (是否有效, 错误消息列表)
        """
        return DatabaseUtils.validate_model_data(model_class, data)
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")
        self._initialized = False
    
    def __enter__(self):
        """上下文管理器入口"""
        if not self._initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def __del__(self):
        """析构函数"""
        self.close()


# 全局数据库客户端实例
_db_client: Optional[DatabaseClient] = None


def get_database_client(config: Optional[DatabaseConfig] = None) -> DatabaseClient:
    """
    获取数据库客户端实例（单例模式）
    
    Args:
        config: 数据库配置
        
    Returns:
        数据库客户端实例
    """
    global _db_client
    
    if _db_client is None:
        _db_client = DatabaseClient(config)
        if not _db_client.initialize():
            raise RuntimeError("数据库客户端初始化失败")
    
    return _db_client


def close_database_client():
    """关闭全局数据库客户端"""
    global _db_client
    
    if _db_client:
        _db_client.close()
        _db_client = None 