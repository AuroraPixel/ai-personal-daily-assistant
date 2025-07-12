"""
用户偏好设置数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Index, UniqueConstraint
from sqlalchemy.sql import func
from core.database_core import BaseModel


class UserPreference(BaseModel):
    """
    用户偏好设置模型
    
    存储用户的个人偏好设置，用户信息来自JSONPlaceholder API
    """
    __tablename__ = 'user_preferences'
    
    # 用户ID（来自JSONPlaceholder API，不存储用户信息）
    user_id = Column(Integer, nullable=False, comment='用户ID（来自JSONPlaceholder）')
    
    # 偏好设置内容（JSON字符串）
    preferences = Column(Text, nullable=False, comment='偏好设置内容（JSON字符串）')
    
    # 偏好设置类型/分类（可选）
    category = Column(String(50), default='general', comment='偏好设置类型')
    
    # 最后更新时间（自动更新）
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), comment='最后更新时间')
    
    # 创建索引和唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'category', name='uk_user_category'),
        Index('idx_user_preferences_user_id', 'user_id'),
        Index('idx_user_preferences_category', 'category'),
        Index('idx_user_preferences_last_updated', 'last_updated'),
    )
    
    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, category={self.category})>"
    
    def to_dict(self):
        """转换为字典格式"""
        # 直接使用基类的to_dict方法，它已经安全处理了datetime字段
        return super().to_dict()
    
    @classmethod
    def create_from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            user_id=data.get('user_id'),
            preferences=data.get('preferences', '{}'),
            category=data.get('category', 'general')
        ) 