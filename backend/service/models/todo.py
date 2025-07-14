"""
待办事项数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database_core import BaseModel


class Todo(BaseModel):
    """
    待办事项模型
    
    存储用户的待办事项，可以关联到笔记
    """
    __tablename__ = 'todos'
    
    # 用户ID（来自JSONPlaceholder API）
    user_id = Column(Integer, nullable=False, comment='用户ID（来自JSONPlaceholder）')
    
    # 待办事项标题
    title = Column(String(200), nullable=False, comment='待办事项标题')
    
    # 待办事项描述
    description = Column(Text, comment='待办事项描述')
    
    # 完成状态
    completed = Column(Boolean, default=False, comment='是否完成')
    
    # 优先级（high, medium, low）
    priority = Column(String(10), default='medium', comment='优先级')
    
    # 关联的笔记ID（业务逻辑关联，无外键约束）
    note_id = Column(Integer, comment='关联的笔记ID（业务逻辑关联）')
    
    # 截止日期
    due_date = Column(DateTime, comment='截止日期')
    
    # 完成时间
    completed_at = Column(DateTime, comment='完成时间')
    
    # 最后更新时间
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), comment='最后更新时间')
    
    # 注释：移除外键关联关系，改为使用业务逻辑查询
    # note = relationship("Note", backref="todos")
    
    # 创建索引优化查询
    __table_args__ = (
        Index('idx_todos_user_id', 'user_id'),
        Index('idx_todos_completed', 'completed'),
        Index('idx_todos_priority', 'priority'),
        Index('idx_todos_due_date', 'due_date'),
        Index('idx_todos_note_id', 'note_id'),
        Index('idx_todos_user_completed', 'user_id', 'completed'),
        Index('idx_todos_user_priority', 'user_id', 'priority'),
    )
    
    def __repr__(self):
        return f"<Todo(id={self.id}, user_id={self.user_id}, title='{self.title[:30]}...', completed={self.completed})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return super().to_dict()
    
    @classmethod
    def create_from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            user_id=data.get('user_id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            completed=data.get('completed', False),
            priority=data.get('priority', 'medium'),
            note_id=data.get('note_id'),
            due_date=data.get('due_date')
        )
    
    def mark_completed(self):
        """标记为完成"""
        self.completed = True
        self.completed_at = func.now()
    
    def mark_pending(self):
        """标记为待完成"""
        self.completed = False
        self.completed_at = None
    
    def is_overdue(self):
        """检查是否过期"""
        due_date_value = getattr(self, 'due_date', None)
        completed_value = getattr(self, 'completed', False)
        
        if not due_date_value or completed_value:
            return False
        
        from datetime import datetime
        return datetime.now() > due_date_value
    
    def get_priority_level(self):
        """获取优先级数值（用于排序）"""
        priority_map = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        priority_value = getattr(self, 'priority', 'medium')
        return priority_map.get(priority_value, 2)
    
    def get_status_display(self):
        """获取状态显示文本"""
        completed_value = getattr(self, 'completed', False)
        
        if completed_value:
            return '已完成'
        elif self.is_overdue():
            return '已过期'
        else:
            return '进行中' 