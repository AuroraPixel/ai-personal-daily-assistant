"""
笔记数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from core.database_core import BaseModel


class InvalidTagError(Exception):
    """标签验证异常"""
    pass


class Note(BaseModel):
    """
    笔记模型
    
    存储用户的笔记内容，用户信息来自JSONPlaceholder API
    """
    __tablename__ = 'notes'
    
    # 允许的标签选项
    ALLOWED_TAGS = [
        'lifestyle tips',
        'cooking advice',
        'weather interpretation',
        'news context'
    ]
    
    # 用户ID（来自JSONPlaceholder API）
    user_id = Column(Integer, nullable=False, comment='用户ID（来自JSONPlaceholder）')
    
    # 笔记标题
    title = Column(String(200), nullable=False, comment='笔记标题')
    
    # 笔记内容
    content = Column(Text, comment='笔记内容')
    
    # 笔记标签（单个标签，只允许指定选项）
    tag = Column(String(50), comment='笔记标签')
    
    # 笔记状态（草稿、已发布、已归档等）
    status = Column(String(20), default='draft', comment='笔记状态')
    
    # 最后更新时间
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), comment='最后更新时间')
    
    # 创建索引优化查询
    __table_args__ = (
        Index('idx_notes_user_id', 'user_id'),
        Index('idx_notes_title', 'title'),
        Index('idx_notes_status', 'status'),
        Index('idx_notes_tag', 'tag'),
        Index('idx_notes_last_updated', 'last_updated'),
        Index('idx_notes_user_status', 'user_id', 'status'),
    )
    
    def __repr__(self):
        return f"<Note(id={self.id}, user_id={self.user_id}, title='{self.title[:30]}...')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return super().to_dict()
    
    @classmethod
    def validate_tag(cls, tag):
        """验证标签是否有效"""
        if tag is None:
            return True  # 允许空标签
        
        if tag not in cls.ALLOWED_TAGS:
            raise InvalidTagError(
                f"Invalid tag '{tag}'. Allowed tags are: {', '.join(cls.ALLOWED_TAGS)}"
            )
        return True
    
    @classmethod
    def create_from_dict(cls, data):
        """从字典创建实例"""
        tag = data.get('tag', '')
        
        # 验证标签
        if tag:
            cls.validate_tag(tag)
        
        return cls(
            user_id=data.get('user_id'),
            title=data.get('title', ''),
            content=data.get('content', ''),
            tag=tag,
            status=data.get('status', 'draft')
        )
    
    def set_tag(self, tag):
        """设置标签"""
        if tag:
            self.validate_tag(tag)
        self.tag = tag
    
    def get_tag(self):
        """获取标签"""
        return getattr(self, 'tag', None)
    
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