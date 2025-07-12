"""
数据模型基类
"""

from datetime import datetime
from typing import Any, Dict, Optional, List
from sqlalchemy import Column, Integer, DateTime, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """SQLAlchemy声明式基类"""
    pass


class BaseModel(Base):
    """
    数据模型基类
    提供通用的字段和方法
    """
    __abstract__ = True
    
    # 通用字段
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将模型实例转换为字典
        
        Returns:
            模型数据字典
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        从字典更新模型实例
        
        Args:
            data: 更新数据字典
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        从字典创建模型实例
        
        Args:
            data: 创建数据字典
            
        Returns:
            模型实例
        """
        # 过滤掉不存在的字段
        filtered_data = {
            key: value for key, value in data.items()
            if key in cls.__table__.columns.keys()
        }
        return cls(**filtered_data)
    
    def __repr__(self) -> str:
        """模型实例的字符串表示"""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"


class ModelManager:
    """
    模型管理器
    提供模型的CRUD操作
    """
    
    def __init__(self, model_class: type):
        """
        初始化模型管理器
        
        Args:
            model_class: 模型类
        """
        self.model_class = model_class
    
    def create(self, session, **kwargs) -> BaseModel:
        """
        创建新记录
        
        Args:
            session: 数据库会话
            **kwargs: 创建参数
            
        Returns:
            创建的模型实例
        """
        instance = self.model_class(**kwargs)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance
    
    def get_by_id(self, session, record_id: int) -> Optional[BaseModel]:
        """
        通过ID获取记录
        
        Args:
            session: 数据库会话
            record_id: 记录ID
            
        Returns:
            模型实例或None
        """
        return session.query(self.model_class).filter(
            self.model_class.id == record_id
        ).first()
    
    def get_all(self, session, limit: int = 100, offset: int = 0) -> List[BaseModel]:
        """
        获取所有记录
        
        Args:
            session: 数据库会话
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            模型实例列表
        """
        return session.query(self.model_class).offset(offset).limit(limit).all()
    
    def update(self, session, record_id: int, **kwargs) -> Optional[BaseModel]:
        """
        更新记录
        
        Args:
            session: 数据库会话
            record_id: 记录ID
            **kwargs: 更新参数
            
        Returns:
            更新后的模型实例或None
        """
        instance = self.get_by_id(session, record_id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            session.commit()
            session.refresh(instance)
        return instance
    
    def delete(self, session, record_id: int) -> bool:
        """
        删除记录
        
        Args:
            session: 数据库会话
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        instance = self.get_by_id(session, record_id)
        if instance:
            session.delete(instance)
            session.commit()
            return True
        return False
    
    def count(self, session) -> int:
        """
        获取记录总数
        
        Args:
            session: 数据库会话
            
        Returns:
            记录总数
        """
        return session.query(self.model_class).count() 