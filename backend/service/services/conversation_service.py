"""
会话管理服务

管理用户会话，包括创建、更新、删除、查询等操作
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from core.database_core import DatabaseClient
from ..models.conversation import Conversation
from .user_service import UserService


class ConversationService:
    """
    会话管理服务类
    
    管理用户的会话数据
    """
    
    def __init__(self, db_client: Optional[DatabaseClient] = None):
        """
        初始化会话管理服务
        
        Args:
            db_client: 数据库客户端，如果未提供则创建新实例
        """
        self.db_client = db_client or DatabaseClient()
        self.user_service = UserService()
        
        # 确保数据库初始化
        if not self.db_client._initialized:
            self.db_client.initialize()
    
    def create_conversation(self, user_id: int, title: str, description: str = '', 
                          status: str = Conversation.STATUS_ACTIVE, id_str: Optional[str] = None) -> Optional[Conversation]:
        """
        创建新会话
        
        Args:
            user_id: 用户ID
            title: 会话标题
            description: 会话描述
            status: 会话状态
            id_str: 自定义会话UUID（可选，不提供时自动生成）
            
        Returns:
            创建的会话对象，失败时返回None
        """
        try:
            # 验证用户是否存在
            user = self.user_service.get_user(user_id)
            if not user:
                raise ValueError(f"用户不存在: {user_id}")
            
            # 创建会话对象
            conversation_data = {
                'user_id': user_id,
                'title': title,
                'description': description,
                'status': status
            }
            
            # 如果提供了自定义id_str，则添加到数据中
            if id_str is not None:
                conversation_data['id_str'] = id_str
            
            conversation = Conversation.create_from_dict(conversation_data)
            
            # 保存到数据库
            with self.db_client.get_session() as session:
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                
            return conversation
            
        except Exception as e:
            print(f"创建会话失败: {e}")
            return None
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """
        根据ID获取会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            会话对象，未找到时返回None
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if conversation:
                    return conversation
                
                return None
                
        except Exception as e:
            print(f"获取会话失败: {e}")
            return None
    
    def get_conversation_by_id_str(self, conversation_id_str: str) -> Optional[Conversation]:
        """
        根据字符串ID获取会话
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            
        Returns:
            会话对象，未找到时返回None
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id_str == conversation_id_str
                ).first()
                
                if conversation:
                    return conversation
                
                return None
                
        except Exception as e:
            print(f"获取会话失败: {e}")
            return None
    
    def get_user_conversations(self, user_id: int, status: Optional[str] = None,
                             limit: int = 50, offset: int = 0) -> List[Conversation]:
        """
        获取用户的会话列表
        
        Args:
            user_id: 用户ID
            status: 会话状态过滤（可选）
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            会话列表
        """
        try:
            with self.db_client.get_session() as session:
                query = session.query(Conversation).filter(
                    Conversation.user_id == user_id
                )
                
                if status:
                    query = query.filter(Conversation.status == status)
                
                conversations = query.order_by(desc(Conversation.last_active))\
                                   .limit(limit)\
                                   .offset(offset)\
                                   .all()
                
                return conversations
                
        except Exception as e:
            print(f"获取用户会话列表失败: {e}")
            return []
    
    def update_conversation(self, conversation_id: int, title: Optional[str] = None,
                          description: Optional[str] = None, status: Optional[str] = None) -> Optional[Conversation]:
        """
        更新会话信息
        
        Args:
            conversation_id: 会话ID
            title: 新标题（可选）
            description: 新描述（可选）
            status: 新状态（可选）
            
        Returns:
            更新后的会话对象，失败时返回None
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if not conversation:
                    return None
                
                # 更新字段
                if title is not None:
                    conversation.title = title
                if description is not None:
                    conversation.description = description
                if status is not None:
                    if status not in Conversation.ALLOWED_STATUS:
                        raise ValueError(f"无效的状态: {status}")
                    conversation.status = status
                
                session.commit()
                session.refresh(conversation)
                return conversation
                
        except Exception as e:
            print(f"更新会话失败: {e}")
            return None
    
    def update_conversation_by_id_str(self, conversation_id_str: str, title: Optional[str] = None,
                                    description: Optional[str] = None, status: Optional[str] = None) -> Optional[Conversation]:
        """
        根据字符串ID更新会话信息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            title: 新标题（可选）
            description: 新描述（可选）
            status: 新状态（可选）
            
        Returns:
            更新后的会话对象，失败时返回None
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id_str == conversation_id_str
                ).first()
                
                if not conversation:
                    return None
                
                # 更新字段
                if title is not None:
                    conversation.title = title
                if description is not None:
                    conversation.description = description
                if status is not None:
                    if status not in Conversation.ALLOWED_STATUS:
                        raise ValueError(f"无效的状态: {status}")
                    conversation.status = status
                
                session.commit()
                session.refresh(conversation)
                return conversation
                
        except Exception as e:
            print(f"更新会话失败: {e}")
            return None
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """
        删除会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            删除成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if not conversation:
                    return False
                
                session.delete(conversation)
                session.commit()
                return True
                
        except Exception as e:
            print(f"删除会话失败: {e}")
            return False
    
    def delete_conversation_by_id_str(self, conversation_id_str: str) -> bool:
        """
        根据字符串ID删除会话
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            
        Returns:
            删除成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id_str == conversation_id_str
                ).first()
                
                if not conversation:
                    return False
                
                session.delete(conversation)
                session.commit()
                return True
                
        except Exception as e:
            print(f"删除会话失败: {e}")
            return False
    
    def search_conversations(self, user_id: int, query: str, limit: int = 20) -> List[Conversation]:
        """
        搜索用户的会话
        
        Args:
            user_id: 用户ID
            query: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            匹配的会话列表
        """
        try:
            with self.db_client.get_session() as session:
                conversations = session.query(Conversation).filter(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.title.contains(query)
                    )
                ).order_by(desc(Conversation.last_active))\
                .limit(limit)\
                .all()
                
                return conversations
                
        except Exception as e:
            print(f"搜索会话失败: {e}")
            return []
    
    def get_active_conversations(self, user_id: int, limit: int = 10) -> List[Conversation]:
        """
        获取用户的活跃会话
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            活跃会话列表
        """
        return self.get_user_conversations(
            user_id=user_id,
            status=Conversation.STATUS_ACTIVE,
            limit=limit
        )
    
    def archive_conversation(self, conversation_id: int) -> bool:
        """
        归档会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            归档成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if not conversation:
                    return False
                
                conversation.status = Conversation.STATUS_ARCHIVED
                session.commit()
                return True
                
        except Exception as e:
            print(f"归档会话失败: {e}")
            return False
    
    def archive_conversation_by_id_str(self, conversation_id_str: str) -> bool:
        """
        根据字符串ID归档会话
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            
        Returns:
            归档成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id_str == conversation_id_str
                ).first()
                
                if not conversation:
                    return False
                
                conversation.status = Conversation.STATUS_ARCHIVED
                session.commit()
                return True
                
        except Exception as e:
            print(f"归档会话失败: {e}")
            return False
    
    def activate_conversation(self, conversation_id: int) -> bool:
        """
        激活会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            激活成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if not conversation:
                    return False
                
                conversation.status = Conversation.STATUS_ACTIVE
                session.commit()
                return True
                
        except Exception as e:
            print(f"激活会话失败: {e}")
            return False
    
    def activate_conversation_by_id_str(self, conversation_id_str: str) -> bool:
        """
        根据字符串ID激活会话
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            
        Returns:
            激活成功返回True，否则返回False
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id_str == conversation_id_str
                ).first()
                
                if not conversation:
                    return False
                
                conversation.status = Conversation.STATUS_ACTIVE
                session.commit()
                return True
                
        except Exception as e:
            print(f"激活会话失败: {e}")
            return False
    
    def get_conversation_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户会话统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含统计信息的字典
        """
        try:
            with self.db_client.get_session() as session:
                # 总会话数
                total_count = session.query(Conversation).filter(
                    Conversation.user_id == user_id
                ).count()
                
                # 活跃会话数
                active_count = session.query(Conversation).filter(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.status == Conversation.STATUS_ACTIVE
                    )
                ).count()
                
                # 归档会话数
                archived_count = session.query(Conversation).filter(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.status == Conversation.STATUS_ARCHIVED
                    )
                ).count()
                
                # 停用会话数
                inactive_count = session.query(Conversation).filter(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.status == Conversation.STATUS_INACTIVE
                    )
                ).count()
                
                return {
                    'total_conversations': total_count,
                    'active_conversations': active_count,
                    'archived_conversations': archived_count,
                    'inactive_conversations': inactive_count
                }
                
        except Exception as e:
            print(f"获取会话统计失败: {e}")
            return {
                'total_conversations': 0,
                'active_conversations': 0,
                'archived_conversations': 0,
                'inactive_conversations': 0
            }
    
    def get_conversation_summary(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        获取会话摘要信息
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            包含摘要信息的字典，失败时返回None
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if not conversation:
                    return None
                
                # 获取消息数量
                from ..models.chat_message import ChatMessage
                message_count = session.query(ChatMessage).filter(
                    ChatMessage.conversation_id == conversation_id
                ).count()
                
                return {
                    'id': conversation.id,
                    'id_str': conversation.id_str,
                    'title': conversation.title,
                    'description': conversation.description,
                    'status': conversation.status,
                    'message_count': message_count,
                    'last_active': conversation.last_active,
                    'created_at': conversation.created_at
                }
                
        except Exception as e:
            print(f"获取会话摘要失败: {e}")
            return None
    
    def get_conversation_summary_by_id_str(self, conversation_id_str: str) -> Optional[Dict[str, Any]]:
        """
        根据字符串ID获取会话摘要信息
        
        Args:
            conversation_id_str: 会话字符串ID（UUID）
            
        Returns:
            包含摘要信息的字典，失败时返回None
        """
        try:
            with self.db_client.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.id_str == conversation_id_str
                ).first()
                
                if not conversation:
                    return None
                
                # 获取消息数量
                from ..models.chat_message import ChatMessage
                message_count = session.query(ChatMessage).filter(
                    ChatMessage.conversation_id_str == conversation_id_str
                ).count()
                
                return {
                    'id': conversation.id,
                    'id_str': conversation.id_str,
                    'title': conversation.title,
                    'description': conversation.description,
                    'status': conversation.status,
                    'message_count': message_count,
                    'last_active': conversation.last_active,
                    'created_at': conversation.created_at
                }
                
        except Exception as e:
            print(f"获取会话摘要失败: {e}")
            return None
    
    def close(self):
        """
        关闭数据库连接
        """
        if self.db_client:
            self.db_client.close() 