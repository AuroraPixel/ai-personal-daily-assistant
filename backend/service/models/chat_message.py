"""
聊天记录数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database_core import BaseModel


class ChatMessage(BaseModel):
    """
    聊天记录模型
    
    存储会话中的聊天消息
    """
    __tablename__ = 'chat_messages'
    
    # 发送者类型常量
    SENDER_TYPE_HUMAN = 'human'
    SENDER_TYPE_AI = 'ai'
    SENDER_TYPE_TOOL = 'tool'
    SENDER_TYPE_SYSTEM = 'system'
    SENDER_TYPE_API = 'api'
    SENDER_TYPE_WEBHOOK = 'webhook'
    
    ALLOWED_SENDER_TYPES = [
        SENDER_TYPE_HUMAN,
        SENDER_TYPE_AI,
        SENDER_TYPE_TOOL,
        SENDER_TYPE_SYSTEM,
        SENDER_TYPE_API,
        SENDER_TYPE_WEBHOOK
    ]
    
    # 消息状态常量
    STATUS_SENT = 'sent'
    STATUS_DELIVERED = 'delivered'
    STATUS_READ = 'read'
    STATUS_FAILED = 'failed'
    
    ALLOWED_STATUS = [
        STATUS_SENT,
        STATUS_DELIVERED,
        STATUS_READ,
        STATUS_FAILED
    ]
    
    # 会话ID（业务逻辑关联，无外键约束）
    conversation_id = Column(Integer, nullable=False, comment='会话ID（业务逻辑关联）')
    
    # 会话字符串标识符（业务逻辑关联，无外键约束）
    conversation_id_str = Column(String(36), nullable=False, comment='会话字符串标识符（业务逻辑关联）')
    
    # 发送者类型
    sender_type = Column(String(20), nullable=False, comment='发送者类型')
    
    # 发送者标识（可选，用于区分不同的发送者）
    sender_id = Column(String(100), comment='发送者标识')
    
    # 消息内容
    content = Column(Text, nullable=False, comment='消息内容')
    
    # 消息类型（文本、图片、文件等）
    message_type = Column(String(20), default='text', comment='消息类型')
    
    # 消息状态
    status = Column(String(20), default=STATUS_SENT, comment='消息状态')
    
    # 元数据（JSON格式存储额外信息）
    extra_data = Column(Text, comment='元数据（JSON格式）')
    
    # 回复的消息ID（业务逻辑关联，无外键约束）
    reply_to_id = Column(Integer, comment='回复的消息ID（业务逻辑关联）')
    
    # 注释：关联关系移除，改为使用业务逻辑查询
    # conversation = relationship("Conversation", back_populates="messages", foreign_keys=[conversation_id])
    # reply_to = relationship("ChatMessage", remote_side='ChatMessage.id')
    
    # 创建索引优化查询
    __table_args__ = (
        Index('idx_chat_message_conversation_id', 'conversation_id'),
        Index('idx_chat_message_conversation_id_str', 'conversation_id_str'),
        Index('idx_chat_message_sender_type', 'sender_type'),
        Index('idx_chat_message_sender_id', 'sender_id'),
        Index('idx_chat_message_created_at', 'created_at'),
        Index('idx_chat_message_status', 'status'),
        Index('idx_chat_message_reply_to_id', 'reply_to_id'),
    )
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, conversation_id={self.conversation_id}, sender_type='{self.sender_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'conversation_id_str': self.conversation_id_str,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'content': self.content,
            'message_type': self.message_type,
            'status': self.status,
            'extra_data': self.extra_data,
            'reply_to_id': self.reply_to_id,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }
    
    @classmethod
    def validate_sender_type(cls, sender_type):
        """验证发送者类型"""
        if sender_type not in cls.ALLOWED_SENDER_TYPES:
            raise ValueError(f"Invalid sender_type: {sender_type}. Allowed values: {cls.ALLOWED_SENDER_TYPES}")
        return True
    
    @classmethod
    def validate_status(cls, status):
        """验证消息状态"""
        if status not in cls.ALLOWED_STATUS:
            raise ValueError(f"Invalid status: {status}. Allowed values: {cls.ALLOWED_STATUS}")
        return True
    
    @classmethod
    def create_from_dict(cls, data):
        """从字典创建消息对象"""
        # 验证必填字段
        if 'conversation_id' not in data:
            raise ValueError("conversation_id is required")
        if 'conversation_id_str' not in data:
            raise ValueError("conversation_id_str is required")
        if 'sender_type' not in data:
            raise ValueError("sender_type is required")
        if 'content' not in data:
            raise ValueError("content is required")
        
        # 验证发送者类型
        cls.validate_sender_type(data['sender_type'])
        
        # 验证状态
        status = data.get('status', cls.STATUS_SENT)
        cls.validate_status(status)
        
        # 创建对象
        message = cls(
            conversation_id=data['conversation_id'],
            conversation_id_str=data['conversation_id_str'],
            sender_type=data['sender_type'],
            sender_id=data.get('sender_id'),
            content=data['content'],
            message_type=data.get('message_type', 'text'),
            status=status,
            extra_data=data.get('extra_data'),
            reply_to_id=data.get('reply_to_id')
        )
        
        return message
    
    def set_status(self, status):
        """设置消息状态"""
        self.validate_status(status)
        self.status = status
    
    def get_status(self):
        """获取消息状态"""
        return self.status
    
    def is_human_message(self):
        """检查是否为人类消息"""
        return self.sender_type == self.SENDER_TYPE_HUMAN
    
    def is_ai_message(self):
        """检查是否为AI消息"""
        return self.sender_type == self.SENDER_TYPE_AI
    
    def is_tool_message(self):
        """检查是否为工具消息"""
        return self.sender_type == self.SENDER_TYPE_TOOL
    
    def is_system_message(self):
        """检查是否为系统消息"""
        return self.sender_type == self.SENDER_TYPE_SYSTEM
    
    def mark_as_read(self):
        """标记消息为已读"""
        self.set_status(self.STATUS_READ)
    
    def mark_as_delivered(self):
        """标记消息为已送达"""
        self.set_status(self.STATUS_DELIVERED)
    
    def mark_as_failed(self):
        """标记消息为失败"""
        self.set_status(self.STATUS_FAILED)
    
    def get_content_preview(self, max_length=100):
        """获取消息内容预览"""
        content_value = getattr(self, 'content', None)
        if content_value is None or content_value == "":
            return ""
        if len(content_value) <= max_length:
            return content_value
        return content_value[:max_length] + "..." 