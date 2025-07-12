"""
笔记服务

管理用户笔记，包括创建、更新、删除、搜索等操作
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from core.database_core import DatabaseClient
from core.vector_core import ChromaVectorClient, VectorConfig, VectorDocument, VectorDeleteFilter
from ..models.note import Note, InvalidTagError
from .user_service import UserService


class NoteService:
    """
    笔记服务类
    
    管理用户的笔记数据，并同步到向量数据库
    """
    
    def __init__(self, db_client: Optional[DatabaseClient] = None, vector_client: Optional[ChromaVectorClient] = None):
        """
        初始化笔记服务
        
        Args:
            db_client: 数据库客户端，如果未提供则创建新实例
            vector_client: 向量数据库客户端，如果未提供则创建新实例
        """
        self.db_client = db_client or DatabaseClient()
        self.user_service = UserService()
        
        # 初始化向量数据库客户端
        try:
            if vector_client:
                self.vector_client = vector_client
            else:
                config = VectorConfig.from_env()
                self.vector_client = ChromaVectorClient(config)
        except Exception as e:
            print(f"警告：向量数据库初始化失败: {e}")
            self.vector_client = None
        
        # 确保数据库初始化
        if not self.db_client._initialized:
            self.db_client.initialize()
    
    def create_note(self, user_id: int, title: str, content: str = '', 
                   tag: Optional[str] = None, status: str = 'draft') -> Optional[Note]:
        """
        创建新笔记
        
        Args:
            user_id: 用户ID
            title: 笔记标题
            content: 笔记内容
            tag: 笔记标签（单个标签）
            status: 笔记状态
            
        Returns:
            创建的笔记对象或None
        """
        try:
            # 验证用户是否存在
            if not self.user_service.validate_user_exists(user_id):
                print(f"用户 {user_id} 不存在")
                return None
            
            # 验证标签
            if tag is not None and tag != '':
                Note.validate_tag(tag)
            
            with self.db_client.get_session() as session:
                note = Note(
                    user_id=user_id,
                    title=title,
                    content=content,
                    tag=tag,
                    status=status
                )
                
                session.add(note)
                session.commit()
                session.refresh(note)
                
                # 添加到向量数据库
                note_content = getattr(note, 'content', '') or ''
                if self.vector_client and note_content:
                    self._add_to_vector_db(note)
                
                return note
                
        except InvalidTagError as e:
            print(f"创建笔记失败 - 标签验证错误: {e}")
            return None
        except Exception as e:
            print(f"创建笔记失败: {e}")
            return None
    
    def _add_to_vector_db(self, note: Note):
        """添加笔记到向量数据库"""
        try:
            if not self.vector_client:
                return
            
            # 获取实际的值
            note_content = getattr(note, 'content', '') or ''
            note_title = getattr(note, 'title', '') or ''
            note_tag = getattr(note, 'tag', '') or ''
            
            # 准备向量文档
            vector_doc = VectorDocument(
                id=f"note_{note.id}",
                text=f"{note_title}\n{note_content}",
                metadata={
                    "user_id": str(note.user_id),
                    "note_id": str(note.id),
                    "tag": note_tag,
                    "status": note.status,
                    "title": note_title
                },
                user_id=str(note.user_id),
                source="notes"
            )
            
            # 添加到向量数据库
            self.vector_client.add_document(vector_doc)
            print(f"笔记 {note.id} 已添加到向量数据库")
            
        except Exception as e:
            print(f"添加笔记到向量数据库失败: {e}")
    
    def _update_vector_db(self, note: Note):
        """更新向量数据库中的笔记"""
        try:
            if not self.vector_client:
                return
            
            # 获取实际的值
            note_id = getattr(note, 'id', None)
            user_id = getattr(note, 'user_id', None)
            note_content = getattr(note, 'content', '') or ''
            
            if note_id is None or user_id is None:
                return
                
            # 删除旧的向量文档
            self._delete_from_vector_db(note_id, user_id)
            
            # 添加新的向量文档
            if note_content:
                self._add_to_vector_db(note)
            
        except Exception as e:
            print(f"更新向量数据库失败: {e}")
    
    def _delete_from_vector_db(self, note_id: int, user_id: int):
        """从向量数据库中删除笔记"""
        try:
            if not self.vector_client:
                return
            
            # 使用文档ID删除
            delete_filter = VectorDeleteFilter(
                user_id=str(user_id),
                document_ids=[f"note_{note_id}"],
                source_filter=None,
                metadata_filter=None
            )
            
            deleted_count = self.vector_client.delete_documents(delete_filter)
            print(f"从向量数据库中删除了 {deleted_count} 个文档")
            
        except Exception as e:
            print(f"从向量数据库删除笔记失败: {e}")
    
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
                   tag: Optional[str] = None, status: Optional[str] = None) -> Optional[Note]:
        """
        更新笔记
        
        Args:
            note_id: 笔记ID
            title: 新标题
            content: 新内容
            tag: 新标签
            status: 新状态
            
        Returns:
            更新后的笔记对象或None
        """
        try:
            with self.db_client.get_session() as session:
                note = session.query(Note).filter(Note.id == note_id).first()
                
                if not note:
                    return None
                
                # 验证标签
                if tag is not None:
                    Note.validate_tag(tag)
                
                # 更新字段
                if title is not None:
                    note.title = title
                if content is not None:
                    note.content = content
                if tag is not None:
                    note.tag = tag
                if status is not None:
                    note.status = status
                
                session.commit()
                session.refresh(note)
                
                # 更新向量数据库
                if self.vector_client:
                    self._update_vector_db(note)
                
                return note
                
        except InvalidTagError as e:
            print(f"更新笔记失败 - 标签验证错误: {e}")
            return None
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
                    # 先从向量数据库中删除
                    if self.vector_client:
                        self._delete_from_vector_db(note.id, note.user_id)
                    
                    # 再从关系数据库中删除
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
                    search_conditions.append(Note.tag.contains(query))
                
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
                    Note.tag == tag
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
                tags = session.query(Note.tag).filter(
                    Note.user_id == user_id,
                    Note.tag.isnot(None),
                    Note.tag != ''
                ).distinct().all()
                
                return [tag[0] for tag in tags if tag[0]]
                
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
                status_counts = {}
                status_results = session.query(Note.status, func.count(Note.id)).filter(
                    Note.user_id == user_id
                ).group_by(Note.status).all()
                
                for status, count in status_results:
                    status_counts[status] = count
                
                # 按标签统计
                tag_counts = {}
                tag_results = session.query(Note.tag, func.count(Note.id)).filter(
                    Note.user_id == user_id,
                    Note.tag.isnot(None),
                    Note.tag != ''
                ).group_by(Note.tag).all()
                
                for tag, count in tag_results:
                    tag_counts[tag] = count
                
                # 最近更新的笔记
                recent_notes = session.query(Note).filter(
                    Note.user_id == user_id
                ).order_by(Note.last_updated.desc()).limit(5).all()
                
                # 获取所有标签
                all_tags = self.get_user_tags(user_id)
                
                return {
                    'total_notes': total_notes,
                    'status_counts': status_counts,
                    'tag_counts': tag_counts,
                    'recent_notes': [
                        {
                            'id': note.id,
                            'title': note.title,
                            'tag': note.tag,
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
            'tag': note.tag,
            'status': note.status,
            'created_at': note.created_at.isoformat() if hasattr(note, 'created_at') and getattr(note, 'created_at', None) else None,
            'last_updated': note.last_updated.isoformat() if hasattr(note, 'last_updated') and getattr(note, 'last_updated', None) else None
        }
    
    def search_notes_by_vector(self, user_id: int, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        使用向量数据库搜索笔记
        
        Args:
            user_id: 用户ID
            query: 搜索查询
            limit: 限制数量
            
        Returns:
            搜索结果列表
        """
        try:
            if not self.vector_client:
                return []
            
            from core.vector_core import VectorQuery
            
            # 创建向量查询
            vector_query = VectorQuery(
                query_text=query,
                user_id=str(user_id),
                limit=limit,
                similarity_threshold=0.1,  # 降低阈值以获得更多结果
                source_filter="notes",
                metadata_filter=None,
                include_metadata=True,
                include_distances=True
            )
            
            # 执行查询
            results = self.vector_client.query_documents(vector_query)
            
            # 转换结果
            search_results = []
            for result in results:
                metadata = result.metadata or {}
                search_results.append({
                    'note_id': metadata.get('note_id'),
                    'title': metadata.get('title'),
                    'tag': metadata.get('tag'),
                    'score': result.score,
                    'text_preview': result.text[:200] + '...' if len(result.text) > 200 else result.text
                })
            
            return search_results
            
        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        if self.db_client:
            self.db_client.close() 