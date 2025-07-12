"""
笔记数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from core.database_core import BaseModel


class Note(BaseModel):
    """
    笔记模型
    
    存储用户的笔记内容，用户信息来自JSONPlaceholder API
    """
    __tablename__ = 'notes'
    
    # 用户ID（来自JSONPlaceholder API）
    user_id = Column(Integer, nullable=False, comment='用户ID（来自JSONPlaceholder）')
    
    # 笔记标题
    title = Column(String(200), nullable=False, comment='笔记标题')
    
    # 笔记内容
    content = Column(Text, comment='笔记内容')
    
    # 笔记标签（JSON字符串或逗号分隔）
    tags = Column(String(500), comment='笔记标签')
    
    # 笔记状态（草稿、已发布、已归档等）
    status = Column(String(20), default='draft', comment='笔记状态')
    
    # 最后更新时间
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), comment='最后更新时间')
    
    # 创建索引优化查询
    __table_args__ = (
        Index('idx_notes_user_id', 'user_id'),
        Index('idx_notes_title', 'title'),
        Index('idx_notes_status', 'status'),
        Index('idx_notes_last_updated', 'last_updated'),
        Index('idx_notes_user_status', 'user_id', 'status'),
    )
    
    def __repr__(self):
        return f"<Note(id={self.id}, user_id={self.user_id}, title='{self.title[:30]}...')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return super().to_dict()
    
    @classmethod
    def create_from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            user_id=data.get('user_id'),
            title=data.get('title', ''),
            content=data.get('content', ''),
            tags=data.get('tags', ''),
            status=data.get('status', 'draft')
        )
    
    def get_tags_list(self):
        """获取标签列表"""
        tags_value = getattr(self, 'tags', None)
        if not tags_value:
            return []
        return [tag.strip() for tag in tags_value.split(',') if tag.strip()]
    
    def set_tags_list(self, tags_list):
        """设置标签列表"""
        self.tags = ','.join(tags_list) if tags_list else ''
    
    def get_summary(self, max_length=100):
        """获取笔记摘要"""
        content_value = getattr(self, 'content', None)
        if not content_value:
            return ''
        
        # 移除多余的空白字符
        content = ' '.join(content_value.split())
        
        if len(content) <= max_length:
            return content
        
        return content[:max_length] + '...' 