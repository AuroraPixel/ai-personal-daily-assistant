"""
会话管理数据模型
"""

import uuid
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from core.database_core import BaseModel


class Conversation(BaseModel):
    """
    会话管理模型
    
    存储用户的会话信息
    """
    __tablename__ = 'conversations'
    
    # 会话状态常量
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_ARCHIVED = 'archived'
    
    ALLOWED_STATUS = [
        STATUS_ACTIVE,
        STATUS_INACTIVE,
        STATUS_ARCHIVED
    ]
    
    # 用户ID（来自JSONPlaceholder API）
    user_id = Column(Integer, nullable=False, comment='用户ID（来自JSONPlaceholder）')
    
    # 会话字符串标识符（UUID）
    id_str = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), comment='会话字符串标识符（UUID）')
    
    # 会话标题
    title = Column(String(200), nullable=False, comment='会话标题')
    
    # 会话描述
    description = Column(Text, comment='会话描述')
    
    # 会话状态
    status = Column(String(20), default=STATUS_ACTIVE, comment='会话状态')
    
    # 最后活跃时间
    last_active = Column(DateTime, default=func.now(), onupdate=func.now(), comment='最后活跃时间')
    
    # 创建索引优化查询
    __table_args__ = (
        Index('idx_conversation_user_id', 'user_id'),
        Index('idx_conversation_id_str', 'id_str'),
        Index('idx_conversation_status', 'status'),
        Index('idx_conversation_last_active', 'last_active'),
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, id_str='{self.id_str}', title='{self.title}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'id_str': self.id_str,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'last_active': self.last_active.isoformat() if self.last_active is not None else None,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }
    
    @classmethod
    def validate_status(cls, status):
        """验证会话状态"""
        if status not in cls.ALLOWED_STATUS:
            raise ValueError(f"Invalid status: {status}. Allowed values: {cls.ALLOWED_STATUS}")
        return True
    
    @classmethod
    def create_from_dict(cls, data):
        """从字典创建会话对象"""
        # 验证必填字段
        if 'user_id' not in data:
            raise ValueError("user_id is required")
        if 'title' not in data:
            raise ValueError("title is required")
        
        # 验证状态
        status = data.get('status', cls.STATUS_ACTIVE)
        cls.validate_status(status)
        
        # 创建对象
        conversation = cls(
            user_id=data['user_id'],
            title=data['title'],
            description=data.get('description'),
            status=status,
        )
        
        # 如果提供了 id_str，使用它，否则会自动生成
        if 'id_str' in data:
            conversation.id_str = data['id_str']
        
        return conversation
    
    def set_status(self, status):
        """设置会话状态"""
        self.validate_status(status)
        self.status = status
        self.last_active = func.now()
    
    def get_status(self):
        """获取会话状态"""
        return self.status
    
    def is_active(self):
        """检查会话是否活跃"""
        return self.status == self.STATUS_ACTIVE
    
    def archive(self):
        """归档会话"""
        self.set_status(self.STATUS_ARCHIVED)
    
    def activate(self):
        """激活会话"""
        self.set_status(self.STATUS_ACTIVE)
    
    def deactivate(self):
        """停用会话"""
        self.set_status(self.STATUS_INACTIVE) 