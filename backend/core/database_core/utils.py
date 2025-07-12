"""
数据库工具函数
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from contextlib import contextmanager
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


class DatabaseUtils:
    """数据库工具类"""
    
    @staticmethod
    def test_connection(engine) -> bool:
        """
        测试数据库连接
        
        Args:
            engine: SQLAlchemy引擎
            
        Returns:
            连接是否成功
        """
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("数据库连接测试成功")
                return True
        except SQLAlchemyError as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    @staticmethod
    def get_table_info(engine, table_name: str) -> Optional[Dict[str, Any]]:
        """
        获取数据表信息
        
        Args:
            engine: SQLAlchemy引擎
            table_name: 表名
            
        Returns:
            表信息字典或None
        """
        try:
            inspector = inspect(engine)
            if table_name not in inspector.get_table_names():
                return None
            
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            return {
                'name': table_name,
                'columns': columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys
            }
        except SQLAlchemyError as e:
            logger.error(f"获取表信息失败: {e}")
            return None
    
    @staticmethod
    def get_database_info(engine) -> Optional[Dict[str, Any]]:
        """
        获取数据库信息
        
        Args:
            engine: SQLAlchemy引擎
            
        Returns:
            数据库信息字典或None
        """
        try:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            
            return {
                'tables': table_names,
                'table_count': len(table_names),
                'engine_name': engine.name,
                'url': str(engine.url).replace(engine.url.password or '', '*' * 8)
            }
        except SQLAlchemyError as e:
            logger.error(f"获取数据库信息失败: {e}")
            return None
    
    @staticmethod
    def execute_raw_sql(engine, sql: str, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        执行原生SQL查询
        
        Args:
            engine: SQLAlchemy引擎
            sql: SQL语句
            params: 参数字典
            
        Returns:
            查询结果列表或None
        """
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                if result.returns_rows:
                    return [dict(row._mapping) for row in result]
                return []
        except SQLAlchemyError as e:
            logger.error(f"执行SQL失败: {e}")
            return None
    
    @staticmethod
    def backup_table(engine, table_name: str, backup_table_name: str) -> bool:
        """
        备份数据表
        
        Args:
            engine: SQLAlchemy引擎
            table_name: 源表名
            backup_table_name: 备份表名
            
        Returns:
            备份是否成功
        """
        try:
            sql = f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}"
            with engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
                logger.info(f"表 {table_name} 备份为 {backup_table_name} 成功")
                return True
        except SQLAlchemyError as e:
            logger.error(f"备份表失败: {e}")
            return False
    
    @staticmethod
    def truncate_table(engine, table_name: str) -> bool:
        """
        清空数据表
        
        Args:
            engine: SQLAlchemy引擎
            table_name: 表名
            
        Returns:
            清空是否成功
        """
        try:
            sql = f"TRUNCATE TABLE {table_name}"
            with engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
                logger.info(f"表 {table_name} 清空成功")
                return True
        except SQLAlchemyError as e:
            logger.error(f"清空表失败: {e}")
            return False
    
    @staticmethod
    def get_table_row_count(engine, table_name: str) -> Optional[int]:
        """
        获取表的行数
        
        Args:
            engine: SQLAlchemy引擎
            table_name: 表名
            
        Returns:
            行数或None
        """
        try:
            sql = f"SELECT COUNT(*) as count FROM {table_name}"
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                row = result.fetchone()
                return row[0] if row else None
        except SQLAlchemyError as e:
            logger.error(f"获取表行数失败: {e}")
            return None
    
    @staticmethod
    @contextmanager
    def transaction_scope(session: Session):
        """
        事务作用域上下文管理器
        
        Args:
            session: 数据库会话
        """
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"事务回滚: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def batch_insert(session: Session, model_class, data_list: List[Dict], batch_size: int = 1000) -> bool:
        """
        批量插入数据
        
        Args:
            session: 数据库会话
            model_class: 模型类
            data_list: 数据列表
            batch_size: 批次大小
            
        Returns:
            插入是否成功
        """
        try:
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                objects = [model_class(**data) for data in batch]
                session.bulk_save_objects(objects)
                session.commit()
                logger.info(f"批量插入 {len(batch)} 条记录成功")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"批量插入失败: {e}")
            return False
    
    @staticmethod
    def validate_model_data(model_class, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证模型数据
        
        Args:
            model_class: 模型类
            data: 数据字典
            
        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []
        
        try:
            # 检查必填字段
            required_columns = []
            for col in model_class.__table__.columns:
                # 安全地检查默认值
                try:
                    has_default = bool(col.default)
                except:
                    has_default = False
                
                try:
                    has_server_default = bool(col.server_default)
                except:
                    has_server_default = False
                
                # 检查是否为必填字段
                if not col.nullable and not has_default and not has_server_default:
                    # 排除自动生成的字段
                    if col.name not in ['id', 'created_at', 'updated_at']:
                        required_columns.append(col.name)
            
            # 验证必填字段
            for column in required_columns:
                if column not in data or data[column] is None:
                    errors.append(f"字段 {column} 为必填项")
            
            # 检查字段类型（简化版本）
            for column_name, value in data.items():
                if hasattr(model_class, column_name) and value is not None:
                    # 这里可以添加更多的类型检查逻辑
                    pass
            
        except Exception as e:
            logger.error(f"数据验证过程中发生异常: {e}")
            errors.append(f"数据验证异常: {str(e)}")
        
        return len(errors) == 0, errors 