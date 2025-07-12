"""
笔记服务

管理用户笔记，包括创建、更新、删除、搜索等操作
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from core.database_core import DatabaseClient
from ..models.note import Note
from .user_service import UserService


class NoteService:
    """
    笔记服务类
    
    管理用户的笔记数据
    """
    
    def __init__(self, db_client: Optional[DatabaseClient] = None):
        """
        初始化笔记服务
        
        Args:
            db_client: 数据库客户端，如果未提供则创建新实例
        """
        self.db_client = db_client or DatabaseClient()
        self.user_service = UserService()
        
        # 确保数据库初始化
        if not self.db_client._initialized:
            self.db_client.initialize()
    
    def create_note(self, user_id: int, title: str, content: str = '', 
                   tags: Optional[List[str]] = None, status: str = 'draft') -> Optional[Note]:
        """
        创建新笔记
        
        Args:
            user_id: 用户ID
            title: 笔记标题
            content: 笔记内容
            tags: 标签列表
            status: 笔记状态
            
        Returns:
            创建的笔记对象或None
        """
        try:
            # 验证用户是否存在
            if not self.user_service.validate_user_exists(user_id):
                print(f"用户 {user_id} 不存在")
                return None
            
            with self.db_client.get_session() as session:
                note = Note(
                    user_id=user_id,
                    title=title,
                    content=content,
                    status=status
                )
                
                # 设置标签
                if tags:
                    note.set_tags_list(tags)
                
                session.add(note)
                session.commit()
                session.refresh(note)
                
                return note
                
        except Exception as e:
            print(f"创建笔记失败: {e}")
            return None
    
    def get_note(self, note_id: int) -> Optional[Note]:
        """
        获取笔记
        
        Args:
            note_id: 笔记ID
            
        Returns:
            笔记对象或None
        """
        try:
            with self.db_client.get_session() as session:
                note = session.query(Note).filter(Note.id == note_id).first()
                return note
                
        except Exception as e:
            print(f"获取笔记失败: {e}")
            return None
    
    def get_user_notes(self, user_id: int, status: Optional[str] = None, 
                      limit: int = 50, offset: int = 0) -> List[Note]:
        """
        获取用户的笔记列表
        
        Args:
            user_id: 用户ID
            status: 笔记状态筛选
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            笔记列表
        """
        try:
            with self.db_client.get_session() as session:
                query = session.query(Note).filter(Note.user_id == user_id)
                
                if status:
                    query = query.filter(Note.status == status)
                
                notes = query.order_by(Note.last_updated.desc()).offset(offset).limit(limit).all()
                return notes
                
        except Exception as e:
            print(f"获取用户笔记失败: {e}")
            return []
    
    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None,
                   tags: Optional[List[str]] = None, status: Optional[str] = None) -> Optional[Note]:
        """
        更新笔记
        
        Args:
            note_id: 笔记ID
            title: 新标题
            content: 新内容
            tags: 新标签列表
            status: 新状态
            
        Returns:
            更新后的笔记对象或None
        """
        try:
            with self.db_client.get_session() as session:
                note = session.query(Note).filter(Note.id == note_id).first()
                
                if not note:
                    return None
                
                # 更新字段
                if title is not None:
                    note.title = title
                if content is not None:
                    note.content = content
                if tags is not None:
                    note.set_tags_list(tags)
                if status is not None:
                    note.status = status
                
                session.commit()
                session.refresh(note)
                
                return note
                
        except Exception as e:
            print(f"更新笔记失败: {e}")
            return None
    
    def delete_note(self, note_id: int) -> bool:
        """
        删除笔记
        
        Args:
            note_id: 笔记ID
            
        Returns:
            是否删除成功
        """
        try:
            with self.db_client.get_session() as session:
                note = session.query(Note).filter(Note.id == note_id).first()
                
                if note:
                    session.delete(note)
                    session.commit()
                    return True
                return False
                
        except Exception as e:
            print(f"删除笔记失败: {e}")
            return False
    
    def search_notes(self, user_id: int, query: str, search_in_content: bool = True,
                    search_in_tags: bool = True, limit: int = 20) -> List[Note]:
        """
        搜索笔记
        
        Args:
            user_id: 用户ID
            query: 搜索关键词
            search_in_content: 是否搜索内容
            search_in_tags: 是否搜索标签
            limit: 限制数量
            
        Returns:
            匹配的笔记列表
        """
        try:
            with self.db_client.get_session() as session:
                conditions = [Note.user_id == user_id]
                
                # 构建搜索条件
                search_conditions = []
                
                # 搜索标题
                search_conditions.append(Note.title.contains(query))
                
                # 搜索内容
                if search_in_content:
                    search_conditions.append(Note.content.contains(query))
                
                # 搜索标签
                if search_in_tags:
                    search_conditions.append(Note.tags.contains(query))
                
                # 组合搜索条件
                if search_conditions:
                    conditions.append(or_(*search_conditions))
                
                notes = session.query(Note).filter(and_(*conditions)).order_by(
                    Note.last_updated.desc()
                ).limit(limit).all()
                
                return notes
                
        except Exception as e:
            print(f"搜索笔记失败: {e}")
            return []
    
    def get_notes_by_tag(self, user_id: int, tag: str, limit: int = 20) -> List[Note]:
        """
        根据标签获取笔记
        
        Args:
            user_id: 用户ID
            tag: 标签
            limit: 限制数量
            
        Returns:
            匹配的笔记列表
        """
        try:
            with self.db_client.get_session() as session:
                notes = session.query(Note).filter(
                    Note.user_id == user_id,
                    Note.tags.contains(tag)
                ).order_by(Note.last_updated.desc()).limit(limit).all()
                
                return notes
                
        except Exception as e:
            print(f"根据标签获取笔记失败: {e}")
            return []
    
    def get_user_tags(self, user_id: int) -> List[str]:
        """
        获取用户使用的所有标签
        
        Args:
            user_id: 用户ID
            
        Returns:
            标签列表
        """
        try:
            with self.db_client.get_session() as session:
                notes = session.query(Note.tags).filter(
                    Note.user_id == user_id,
                    Note.tags.isnot(None),
                    Note.tags != ''
                ).all()
                
                all_tags = set()
                for note_tags in notes:
                    if note_tags[0]:  # note_tags是一个元组
                        tags = [tag.strip() for tag in note_tags[0].split(',') if tag.strip()]
                        all_tags.update(tags)
                
                return list(all_tags)
                
        except Exception as e:
            print(f"获取用户标签失败: {e}")
            return []
    
    def get_notes_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取笔记统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        try:
            with self.db_client.get_session() as session:
                # 总笔记数
                total_notes = session.query(Note).filter(Note.user_id == user_id).count()
                
                # 按状态统计
                status_counts = session.query(Note.status, session.query(Note).filter(
                    Note.user_id == user_id
                ).count()).filter(Note.user_id == user_id).group_by(Note.status).all()
                
                # 最近更新的笔记
                recent_notes = session.query(Note).filter(
                    Note.user_id == user_id
                ).order_by(Note.last_updated.desc()).limit(5).all()
                
                # 标签统计
                all_tags = self.get_user_tags(user_id)
                
                return {
                    'total_notes': total_notes,
                    'status_counts': dict(status_counts),
                    'recent_notes': [
                        {
                            'id': note.id,
                            'title': note.title,
                            'last_updated': note.last_updated.isoformat() if hasattr(note, 'last_updated') and getattr(note, 'last_updated', None) else None
                        }
                        for note in recent_notes
                    ],
                    'total_tags': len(all_tags),
                    'tags': all_tags
                }
                
        except Exception as e:
            print(f"获取笔记统计失败: {e}")
            return {}
    
    def archive_note(self, note_id: int) -> bool:
        """
        归档笔记
        
        Args:
            note_id: 笔记ID
            
        Returns:
            是否归档成功
        """
        return self.update_note(note_id, status='archived') is not None
    
    def publish_note(self, note_id: int) -> bool:
        """
        发布笔记
        
        Args:
            note_id: 笔记ID
            
        Returns:
            是否发布成功
        """
        return self.update_note(note_id, status='published') is not None
    
    def get_note_summary(self, note_id: int) -> Optional[Dict[str, Any]]:
        """
        获取笔记摘要信息
        
        Args:
            note_id: 笔记ID
            
        Returns:
            笔记摘要字典或None
        """
        note = self.get_note(note_id)
        if not note:
            return None
        
        return {
            'id': note.id,
            'user_id': note.user_id,
            'title': note.title,
            'summary': note.get_summary(),
            'tags': note.get_tags_list(),
            'status': note.status,
            'created_at': note.created_at.isoformat() if hasattr(note, 'created_at') and getattr(note, 'created_at', None) else None,
            'last_updated': note.last_updated.isoformat() if hasattr(note, 'last_updated') and getattr(note, 'last_updated', None) else None
        }
    
    def close(self):
        """关闭数据库连接"""
        if self.db_client:
            self.db_client.close() 