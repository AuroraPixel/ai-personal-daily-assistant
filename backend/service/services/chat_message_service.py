"""
聊天记录服务

管理会话中的聊天消息，包括创建、更新、删除、查询等操作
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from core.database_core import DatabaseClient
from ..models.chat_message import ChatMessage
from ..models.conversation import Conversation
from .conversation_service import ConversationService


class ChatMessageService:
    """
    聊天记录服务类
    
    管理会话中的聊天消息数据
    """
    
    def __init__(self, db_client: Optional[DatabaseClient] = None):
        """
        初始化聊天记录服务
        
        Args:
            db_client: 数据库客户端，如果未提供则创建新实例
        """
        self.db_client = db_client or DatabaseClient()
        self.conversation_service = ConversationService(db_client)
        
        # 确保数据库初始化
        if not self.db_client._initialized:
            self.db_client.initialize()
    
    def create_message(self, conversation_id: int, sender_type: str, content: str,
                      sender_id: Optional[str] = None, message_type: str = 'text',
                      extra_data: Optional[str] = None, reply_to_id: Optional[int] = None) -> Optional[ChatMessage]:
        """
        创建新的聊天消息
        
        Args:
            conversation_id: 会话ID
            sender_type: 发送者类型
            content: 消息内容
            sender_id: 发送者标识
            message_type: 消息类型
            extra_data: 元数据
            reply_to_id: 回复的消息ID
            
        Returns:
            创建的消息对象，失败时返回None
        """
        try:
            # 验证会话是否存在
            conversation = self.conversation_service.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"会话不存在: {conversation_id}")
            
            # 创建消息对象
            message_data = {
                'conversation_id': conversation_id,
                'conversation_id_str': conversation.id_str,
                'sender_type': sender_type,
                'content': content,
                'sender_id': sender_id,
                'message_type': message_type,
                'extra_data': extra_data,
                'reply_to_id': reply_to_id
            }
            
            message = ChatMessage.create_from_dict(message_data)
            
            # 保存到数据库
            with self.db_client.get_session() as session:
                session.add(message)
                session.commit()
                session.refresh(message)
                
                # 更新会话的最后活跃时间
                conversation_db = session.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                if conversation_db:
                    conversation_db.last_active = func.now()
                    session.commit()
                
                # 刷新对象以确保属性已加载
                session.refresh(message)
                
            return message
            
        except Exception as e:
            print(f"创建消息失败: {e}")
            return None
    
    def create_message_by_id_str(self, conversation_id_str: str, sender_type: str, content: str,
                               sender_id: Optional[str] = None, message_type: str = 'text',
                               extra_data: Optional[str] = None, reply_to_id: Optional[int] = None) -> Optional[ChatMessage]:
        """
        通过会话字符串ID创建新的聊天消息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            sender_type: 发送者类型
            content: 消息内容
            sender_id: 发送者标识
            message_type: 消息类型
            extra_data: 元数据
            reply_to_id: 回复的消息ID
            
        Returns:
            创建的消息对象，失败时返回None
        """
        try:
            # 验证会话是否存在
            conversation = self.conversation_service.get_conversation_by_id_str(conversation_id_str)
            if not conversation:
                raise ValueError(f"会话不存在: {conversation_id_str}")
            
            # 创建消息对象
            message_data = {
                'conversation_id': conversation.id,
                'conversation_id_str': conversation_id_str,
                'sender_type': sender_type,
                'content': content,
                'sender_id': sender_id,
                'message_type': message_type,
                'extra_data': extra_data,
                'reply_to_id': reply_to_id
            }
            
            message = ChatMessage.create_from_dict(message_data)
            
            # 保存到数据库
            with self.db_client.get_session() as session:
                session.add(message)
                session.commit()
                session.refresh(message)
                
                # 更新会话的最后活跃时间
                conversation_db = session.query(Conversation).filter(
                    Conversation.id_str == conversation_id_str
                ).first()
                if conversation_db:
                    conversation_db.last_active = func.now()
                    session.commit()
                
                # 刷新对象以确保属性已加载
                session.refresh(message)
                
            return message
            
        except Exception as e:
            print(f"创建消息失败: {e}")
            return None
    
    def get_message(self, message_id: int) -> Optional[ChatMessage]:
        """
        获取单个消息
        
        Args:
            message_id: 消息ID
            
        Returns:
            消息对象，未找到时返回None
        """
        try:
            with self.db_client.get_session() as session:
                message = session.query(ChatMessage).filter(
                    ChatMessage.id == message_id
                ).first()
                
                if message:
                    return message
                
                return None
                
        except Exception as e:
            print(f"获取消息失败: {e}")
            return None
    
    def get_conversation_messages(self, conversation_id: int, limit: int = 50, 
                                offset: int = 0, order_desc: bool = True) -> List[ChatMessage]:
        """
        获取会话的消息列表
        
        Args:
            conversation_id: 会话ID
            limit: 返回数量限制
            offset: 偏移量
            order_desc: 是否按创建时间倒序
            
        Returns:
            消息列表
        """
        try:
            with self.db_client.get_session() as session:
                query = session.query(ChatMessage).filter(
                    ChatMessage.conversation_id == conversation_id
                )
                
                # 排序
                if order_desc:
                    query = query.order_by(desc(ChatMessage.created_at))
                else:
                    query = query.order_by(ChatMessage.created_at)
                
                messages = query.limit(limit).offset(offset).all()
                
                return messages
                
        except Exception as e:
            print(f"获取会话消息失败: {e}")
            return []
    
    def get_conversation_messages_by_id_str(self, conversation_id_str: str, limit: int = 50, 
                                          offset: int = 0, order_desc: bool = True) -> List[ChatMessage]:
        """
        通过会话字符串ID获取会话的消息列表
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            limit: 返回数量限制
            offset: 偏移量
            order_desc: 是否按创建时间倒序
            
        Returns:
            消息列表
        """
        try:
            with self.db_client.get_session() as session:
                query = session.query(ChatMessage).filter(
                    ChatMessage.conversation_id_str == conversation_id_str
                )
                
                # 排序
                if order_desc:
                    query = query.order_by(desc(ChatMessage.created_at))
                else:
                    query = query.order_by(ChatMessage.created_at)
                
                messages = query.limit(limit).offset(offset).all()
                
                return messages
                
        except Exception as e:
            print(f"获取会话消息失败: {e}")
            return []
    
    def get_messages_by_sender_type(self, conversation_id: int, sender_type: str, 
                                  limit: int = 50) -> List[ChatMessage]:
        """
        根据发送者类型获取消息
        
        Args:
            conversation_id: 会话ID
            sender_type: 发送者类型
            limit: 返回数量限制
            
        Returns:
            消息列表
        """
        try:
            with self.db_client.get_session() as session:
                messages = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id == conversation_id,
                        ChatMessage.sender_type == sender_type
                    )
                ).order_by(desc(ChatMessage.created_at))\
                .limit(limit)\
                .all()
                
                return messages
                
        except Exception as e:
            print(f"获取消息失败: {e}")
            return []
    
    def get_messages_by_sender_type_and_id_str(self, conversation_id_str: str, sender_type: str, 
                                             limit: int = 50) -> List[ChatMessage]:
        """
        通过会话字符串ID和发送者类型获取消息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            sender_type: 发送者类型
            limit: 返回数量限制
            
        Returns:
            消息列表
        """
        try:
            with self.db_client.get_session() as session:
                messages = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id_str == conversation_id_str,
                        ChatMessage.sender_type == sender_type
                    )
                ).order_by(desc(ChatMessage.created_at))\
                .limit(limit)\
                .all()
                
                return messages
                
        except Exception as e:
            print(f"获取消息失败: {e}")
            return []
    
    def update_message(self, message_id: int, content: Optional[str] = None,
                      status: Optional[str] = None, extra_data: Optional[str] = None) -> Optional[ChatMessage]:
        """
        更新消息
        
        Args:
            message_id: 消息ID
            content: 新内容（可选）
            status: 新状态（可选）
            extra_data: 新元数据（可选）
            
        Returns:
            更新后的消息对象，失败时返回None
        """
        try:
            with self.db_client.get_session() as session:
                message = session.query(ChatMessage).filter(
                    ChatMessage.id == message_id
                ).first()
                
                if not message:
                    return None
                
                # 更新字段
                if content is not None:
                    message.content = content
                if status is not None:
                    message.set_status(status)
                if extra_data is not None:
                    message.extra_data = extra_data
                
                session.commit()
                return message
                
        except Exception as e:
            print(f"更新消息失败: {e}")
            return None
    
    def delete_message(self, message_id: int) -> bool:
        """
        删除消息
        
        Args:
            message_id: 消息ID
            
        Returns:
            删除成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                message = session.query(ChatMessage).filter(
                    ChatMessage.id == message_id
                ).first()
                
                if not message:
                    return False
                
                session.delete(message)
                session.commit()
                return True
                
        except Exception as e:
            print(f"删除消息失败: {e}")
            return False
    
    def search_messages(self, conversation_id: int, query: str, 
                       sender_type: Optional[str] = None, limit: int = 20) -> List[ChatMessage]:
        """
        搜索消息
        
        Args:
            conversation_id: 会话ID
            query: 搜索关键词
            sender_type: 发送者类型过滤（可选）
            limit: 返回数量限制
            
        Returns:
            匹配的消息列表
        """
        try:
            with self.db_client.get_session() as session:
                query_filter = and_(
                    ChatMessage.conversation_id == conversation_id,
                    ChatMessage.content.contains(query)
                )
                
                if sender_type:
                    query_filter = and_(
                        query_filter,
                        ChatMessage.sender_type == sender_type
                    )
                
                messages = session.query(ChatMessage).filter(query_filter)\
                    .order_by(desc(ChatMessage.created_at))\
                    .limit(limit)\
                    .all()
                
                return messages
                
        except Exception as e:
            print(f"搜索消息失败: {e}")
            return []
    
    def search_messages_by_id_str(self, conversation_id_str: str, query: str, 
                                sender_type: Optional[str] = None, limit: int = 20) -> List[ChatMessage]:
        """
        通过会话字符串ID搜索消息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            query: 搜索关键词
            sender_type: 发送者类型过滤（可选）
            limit: 返回数量限制
            
        Returns:
            匹配的消息列表
        """
        try:
            with self.db_client.get_session() as session:
                query_filter = and_(
                    ChatMessage.conversation_id_str == conversation_id_str,
                    ChatMessage.content.contains(query)
                )
                
                if sender_type:
                    query_filter = and_(
                        query_filter,
                        ChatMessage.sender_type == sender_type
                    )
                
                messages = session.query(ChatMessage).filter(query_filter)\
                    .order_by(desc(ChatMessage.created_at))\
                    .limit(limit)\
                    .all()
                
                return messages
                
        except Exception as e:
            print(f"搜索消息失败: {e}")
            return []
    
    def get_message_replies(self, message_id: int) -> List[ChatMessage]:
        """
        获取消息的回复
        
        Args:
            message_id: 消息ID
            
        Returns:
            回复消息列表
        """
        try:
            with self.db_client.get_session() as session:
                replies = session.query(ChatMessage).filter(
                    ChatMessage.reply_to_id == message_id
                ).order_by(ChatMessage.created_at).all()
                
                return replies
                
        except Exception as e:
            print(f"获取消息回复失败: {e}")
            return []
    
    def mark_message_as_read(self, message_id: int) -> bool:
        """
        标记消息为已读
        
        Args:
            message_id: 消息ID
            
        Returns:
            标记成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                message = session.query(ChatMessage).filter(
                    ChatMessage.id == message_id
                ).first()
                
                if not message:
                    return False
                
                message.mark_as_read()
                session.commit()
                return True
                
        except Exception as e:
            print(f"标记消息为已读失败: {e}")
            return False
    
    def get_conversation_message_statistics(self, conversation_id: int) -> Dict[str, Any]:
        """
        获取会话的消息统计信息
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            包含统计信息的字典
        """
        try:
            with self.db_client.get_session() as session:
                # 总消息数
                total_count = session.query(ChatMessage).filter(
                    ChatMessage.conversation_id == conversation_id
                ).count()
                
                # 各类型消息数
                human_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id == conversation_id,
                        ChatMessage.sender_type == ChatMessage.SENDER_TYPE_HUMAN
                    )
                ).count()
                
                ai_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id == conversation_id,
                        ChatMessage.sender_type == ChatMessage.SENDER_TYPE_AI
                    )
                ).count()
                
                tool_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id == conversation_id,
                        ChatMessage.sender_type == ChatMessage.SENDER_TYPE_TOOL
                    )
                ).count()
                
                system_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id == conversation_id,
                        ChatMessage.sender_type == ChatMessage.SENDER_TYPE_SYSTEM
                    )
                ).count()
                
                # 各状态消息数
                sent_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id == conversation_id,
                        ChatMessage.status == ChatMessage.STATUS_SENT
                    )
                ).count()
                
                read_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id == conversation_id,
                        ChatMessage.status == ChatMessage.STATUS_READ
                    )
                ).count()
                
                return {
                    'total_messages': total_count,
                    'human_messages': human_count,
                    'ai_messages': ai_count,
                    'tool_messages': tool_count,
                    'system_messages': system_count,
                    'sent_messages': sent_count,
                    'read_messages': read_count
                }
                
        except Exception as e:
            print(f"获取消息统计失败: {e}")
            return {
                'total_messages': 0,
                'human_messages': 0,
                'ai_messages': 0,
                'tool_messages': 0,
                'system_messages': 0,
                'sent_messages': 0,
                'read_messages': 0
            }
    
    def get_conversation_message_statistics_by_id_str(self, conversation_id_str: str) -> Dict[str, Any]:
        """
        通过会话字符串ID获取会话的消息统计信息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            
        Returns:
            包含统计信息的字典
        """
        try:
            with self.db_client.get_session() as session:
                # 总消息数
                total_count = session.query(ChatMessage).filter(
                    ChatMessage.conversation_id_str == conversation_id_str
                ).count()
                
                # 各类型消息数
                human_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id_str == conversation_id_str,
                        ChatMessage.sender_type == ChatMessage.SENDER_TYPE_HUMAN
                    )
                ).count()
                
                ai_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id_str == conversation_id_str,
                        ChatMessage.sender_type == ChatMessage.SENDER_TYPE_AI
                    )
                ).count()
                
                tool_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id_str == conversation_id_str,
                        ChatMessage.sender_type == ChatMessage.SENDER_TYPE_TOOL
                    )
                ).count()
                
                system_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id_str == conversation_id_str,
                        ChatMessage.sender_type == ChatMessage.SENDER_TYPE_SYSTEM
                    )
                ).count()
                
                # 各状态消息数
                sent_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id_str == conversation_id_str,
                        ChatMessage.status == ChatMessage.STATUS_SENT
                    )
                ).count()
                
                read_count = session.query(ChatMessage).filter(
                    and_(
                        ChatMessage.conversation_id_str == conversation_id_str,
                        ChatMessage.status == ChatMessage.STATUS_READ
                    )
                ).count()
                
                return {
                    'total_messages': total_count,
                    'human_messages': human_count,
                    'ai_messages': ai_count,
                    'tool_messages': tool_count,
                    'system_messages': system_count,
                    'sent_messages': sent_count,
                    'read_messages': read_count
                }
                
        except Exception as e:
            print(f"获取消息统计失败: {e}")
            return {
                'total_messages': 0,
                'human_messages': 0,
                'ai_messages': 0,
                'tool_messages': 0,
                'system_messages': 0,
                'sent_messages': 0,
                'read_messages': 0
            }
    
    def get_recent_messages(self, conversation_id: int, limit: int = 10) -> List[ChatMessage]:
        """
        获取最近的消息
        
        Args:
            conversation_id: 会话ID
            limit: 返回数量限制
            
        Returns:
            最近的消息列表
        """
        return self.get_conversation_messages(conversation_id, limit=limit, order_desc=True)
    
    def get_recent_messages_by_id_str(self, conversation_id_str: str, limit: int = 10) -> List[ChatMessage]:
        """
        通过会话字符串ID获取最近的消息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            limit: 返回数量限制
            
        Returns:
            最近的消息列表
        """
        return self.get_conversation_messages_by_id_str(conversation_id_str, limit=limit, order_desc=True)
    
    def get_human_messages(self, conversation_id: int, limit: int = 50) -> List[ChatMessage]:
        """
        获取人类消息
        
        Args:
            conversation_id: 会话ID
            limit: 返回数量限制
            
        Returns:
            人类消息列表
        """
        return self.get_messages_by_sender_type(conversation_id, ChatMessage.SENDER_TYPE_HUMAN, limit)
    
    def get_human_messages_by_id_str(self, conversation_id_str: str, limit: int = 50) -> List[ChatMessage]:
        """
        通过会话字符串ID获取人类消息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            limit: 返回数量限制
            
        Returns:
            人类消息列表
        """
        return self.get_messages_by_sender_type_and_id_str(conversation_id_str, ChatMessage.SENDER_TYPE_HUMAN, limit)
    
    def get_ai_messages(self, conversation_id: int, limit: int = 50) -> List[ChatMessage]:
        """
        获取AI消息
        
        Args:
            conversation_id: 会话ID
            limit: 返回数量限制
            
        Returns:
            AI消息列表
        """
        return self.get_messages_by_sender_type(conversation_id, ChatMessage.SENDER_TYPE_AI, limit)
    
    def get_ai_messages_by_id_str(self, conversation_id_str: str, limit: int = 50) -> List[ChatMessage]:
        """
        通过会话字符串ID获取AI消息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            limit: 返回数量限制
            
        Returns:
            AI消息列表
        """
        return self.get_messages_by_sender_type_and_id_str(conversation_id_str, ChatMessage.SENDER_TYPE_AI, limit)
    
    def get_tool_messages(self, conversation_id: int, limit: int = 50) -> List[ChatMessage]:
        """
        获取工具消息
        
        Args:
            conversation_id: 会话ID
            limit: 返回数量限制
            
        Returns:
            工具消息列表
        """
        return self.get_messages_by_sender_type(conversation_id, ChatMessage.SENDER_TYPE_TOOL, limit)
    
    def get_tool_messages_by_id_str(self, conversation_id_str: str, limit: int = 50) -> List[ChatMessage]:
        """
        通过会话字符串ID获取工具消息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            limit: 返回数量限制
            
        Returns:
            工具消息列表
        """
        return self.get_messages_by_sender_type_and_id_str(conversation_id_str, ChatMessage.SENDER_TYPE_TOOL, limit)
    
    def clear_conversation_messages(self, conversation_id: int) -> bool:
        """
        清空会话的所有消息
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            清空成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                # 删除所有消息
                session.query(ChatMessage).filter(
                    ChatMessage.conversation_id == conversation_id
                ).delete()
                
                session.commit()
                return True
                
        except Exception as e:
            print(f"清空会话消息失败: {e}")
            return False
    
    def clear_conversation_messages_by_id_str(self, conversation_id_str: str) -> bool:
        """
        通过会话字符串ID清空会话的所有消息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            
        Returns:
            清空成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                # 删除所有消息
                session.query(ChatMessage).filter(
                    ChatMessage.conversation_id_str == conversation_id_str
                ).delete()
                
                session.commit()
                return True
                
        except Exception as e:
            print(f"清空会话消息失败: {e}")
            return False
    
    def close(self):
        """
        关闭数据库连接
        """
        if self.db_client:
            self.db_client.close() 