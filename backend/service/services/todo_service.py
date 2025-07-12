"""
待办事项服务

管理用户待办事项，包括创建、更新、删除、关联笔记等操作
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, case
from core.database_core import DatabaseClient
from ..models.todo import Todo
from ..models.note import Note
from .user_service import UserService


class TodoService:
    """
    待办事项服务类
    
    管理用户的待办事项数据
    """
    
    def __init__(self, db_client: Optional[DatabaseClient] = None):
        """
        初始化待办事项服务
        
        Args:
            db_client: 数据库客户端，如果未提供则创建新实例
        """
        self.db_client = db_client or DatabaseClient()
        self.user_service = UserService()
        
        # 确保数据库初始化
        if not self.db_client._initialized:
            self.db_client.initialize()
    
    def create_todo(self, user_id: int, title: str, description: str = '',
                   priority: str = 'medium', due_date: Optional[datetime] = None,
                   note_id: Optional[int] = None) -> Optional[Todo]:
        """
        创建新待办事项
        
        Args:
            user_id: 用户ID
            title: 待办事项标题
            description: 描述
            priority: 优先级 (high, medium, low)
            due_date: 截止日期
            note_id: 关联的笔记ID
            
        Returns:
            创建的待办事项对象或None
        """
        try:
            # 验证用户是否存在
            if not self.user_service.validate_user_exists(user_id):
                print(f"用户 {user_id} 不存在")
                return None
            
            # 验证笔记是否存在（如果提供了note_id）
            if note_id:
                with self.db_client.get_session() as session:
                    note = session.query(Note).filter(
                        Note.id == note_id,
                        Note.user_id == user_id
                    ).first()
                    if not note:
                        print(f"笔记 {note_id} 不存在或不属于用户 {user_id}")
                        return None
            
            with self.db_client.get_session() as session:
                todo = Todo(
                    user_id=user_id,
                    title=title,
                    description=description,
                    priority=priority,
                    due_date=due_date,
                    note_id=note_id
                )
                
                session.add(todo)
                session.commit()
                session.refresh(todo)
                
                return todo
                
        except Exception as e:
            print(f"创建待办事项失败: {e}")
            return None
    
    def get_todo(self, todo_id: int) -> Optional[Todo]:
        """
        获取待办事项
        
        Args:
            todo_id: 待办事项ID
            
        Returns:
            待办事项对象或None
        """
        try:
            with self.db_client.get_session() as session:
                todo = session.query(Todo).filter(Todo.id == todo_id).first()
                return todo
                
        except Exception as e:
            print(f"获取待办事项失败: {e}")
            return None
    
    def get_user_todos(self, user_id: int, completed: Optional[bool] = None,
                      priority: Optional[str] = None, limit: int = 50, 
                      offset: int = 0) -> List[Todo]:
        """
        获取用户的待办事项列表
        
        Args:
            user_id: 用户ID
            completed: 完成状态筛选
            priority: 优先级筛选
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            待办事项列表
        """
        try:
            with self.db_client.get_session() as session:
                query = session.query(Todo).filter(Todo.user_id == user_id)
                
                if completed is not None:
                    query = query.filter(Todo.completed == completed)
                
                if priority:
                    query = query.filter(Todo.priority == priority)
                
                todos = query.order_by(
                    Todo.completed.asc(),  # 未完成的优先显示
                    case(
                        (Todo.due_date.is_(None), 1),
                        else_=0
                    ).asc(),  # 空值在后
                    Todo.due_date.asc(),  # 按截止日期排序
                    Todo.priority.desc()  # 按优先级排序
                ).offset(offset).limit(limit).all()
                
                return todos
                
        except Exception as e:
            print(f"获取用户待办事项失败: {e}")
            return []
    
    def update_todo(self, todo_id: int, title: Optional[str] = None,
                   description: Optional[str] = None, priority: Optional[str] = None,
                   due_date: Optional[datetime] = None, note_id: Optional[int] = None) -> Optional[Todo]:
        """
        更新待办事项
        
        Args:
            todo_id: 待办事项ID
            title: 新标题
            description: 新描述
            priority: 新优先级
            due_date: 新截止日期
            note_id: 新关联笔记ID
            
        Returns:
            更新后的待办事项对象或None
        """
        try:
            with self.db_client.get_session() as session:
                todo = session.query(Todo).filter(Todo.id == todo_id).first()
                
                if not todo:
                    return None
                
                # 更新字段
                if title is not None:
                    todo.title = title
                if description is not None:
                    todo.description = description
                if priority is not None:
                    todo.priority = priority
                if due_date is not None:
                    todo.due_date = due_date
                if note_id is not None:
                    # 验证笔记是否存在
                    note = session.query(Note).filter(
                        Note.id == note_id,
                        Note.user_id == todo.user_id
                    ).first()
                    if note:
                        todo.note_id = note_id
                    else:
                        print(f"笔记 {note_id} 不存在或不属于用户")
                
                session.commit()
                session.refresh(todo)
                
                return todo
                
        except Exception as e:
            print(f"更新待办事项失败: {e}")
            return None
    
    def delete_todo(self, todo_id: int) -> bool:
        """
        删除待办事项
        
        Args:
            todo_id: 待办事项ID
            
        Returns:
            是否删除成功
        """
        try:
            with self.db_client.get_session() as session:
                todo = session.query(Todo).filter(Todo.id == todo_id).first()
                
                if todo:
                    session.delete(todo)
                    session.commit()
                    return True
                return False
                
        except Exception as e:
            print(f"删除待办事项失败: {e}")
            return False
    
    def complete_todo(self, todo_id: int) -> bool:
        """
        完成待办事项
        
        Args:
            todo_id: 待办事项ID
            
        Returns:
            是否操作成功
        """
        try:
            with self.db_client.get_session() as session:
                todo = session.query(Todo).filter(Todo.id == todo_id).first()
                
                if todo:
                    todo.mark_completed()
                    session.commit()
                    return True
                return False
                
        except Exception as e:
            print(f"完成待办事项失败: {e}")
            return False
    
    def uncomplete_todo(self, todo_id: int) -> bool:
        """
        取消完成待办事项
        
        Args:
            todo_id: 待办事项ID
            
        Returns:
            是否操作成功
        """
        try:
            with self.db_client.get_session() as session:
                todo = session.query(Todo).filter(Todo.id == todo_id).first()
                
                if todo:
                    todo.mark_pending()
                    session.commit()
                    return True
                return False
                
        except Exception as e:
            print(f"取消完成待办事项失败: {e}")
            return False
    
    def get_overdue_todos(self, user_id: int) -> List[Todo]:
        """
        获取用户的过期待办事项
        
        Args:
            user_id: 用户ID
            
        Returns:
            过期待办事项列表
        """
        try:
            with self.db_client.get_session() as session:
                now = datetime.now()
                todos = session.query(Todo).filter(
                    Todo.user_id == user_id,
                    Todo.completed == False,
                    Todo.due_date < now
                ).order_by(Todo.due_date.asc()).all()
                
                return todos
                
        except Exception as e:
            print(f"获取过期待办事项失败: {e}")
            return []
    
    def get_todos_by_note(self, note_id: int) -> List[Todo]:
        """
        获取关联到特定笔记的待办事项
        
        Args:
            note_id: 笔记ID
            
        Returns:
            待办事项列表
        """
        try:
            with self.db_client.get_session() as session:
                todos = session.query(Todo).filter(
                    Todo.note_id == note_id
                ).order_by(
                    Todo.completed.asc(),
                    case(
                        (Todo.due_date.is_(None), 1),
                        else_=0
                    ).asc(),
                    Todo.due_date.asc()
                ).all()
                
                return todos
                
        except Exception as e:
            print(f"获取笔记关联待办事项失败: {e}")
            return []
    
    def search_todos(self, user_id: int, query: str, limit: int = 20) -> List[Todo]:
        """
        搜索待办事项
        
        Args:
            user_id: 用户ID
            query: 搜索关键词
            limit: 限制数量
            
        Returns:
            匹配的待办事项列表
        """
        try:
            with self.db_client.get_session() as session:
                # 搜索标题和描述
                todos = session.query(Todo).filter(
                    Todo.user_id == user_id,
                    or_(
                        Todo.title.like(f'%{query}%'),
                        Todo.description.like(f'%{query}%')
                    )
                ).order_by(
                    Todo.completed.asc(),
                    case(
                        (Todo.due_date.is_(None), 1),
                        else_=0
                    ).asc(),
                    Todo.due_date.asc()
                ).limit(limit).all()
                
                return todos
                
        except Exception as e:
            print(f"搜索待办事项失败: {e}")
            return []
    
    def get_todos_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取待办事项统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        try:
            with self.db_client.get_session() as session:
                # 总待办事项数
                total_todos = session.query(Todo).filter(Todo.user_id == user_id).count()
                
                # 已完成数
                completed_todos = session.query(Todo).filter(
                    Todo.user_id == user_id,
                    Todo.completed == True
                ).count()
                
                # 待完成数
                pending_todos = total_todos - completed_todos
                
                # 过期数
                now = datetime.now()
                overdue_todos = session.query(Todo).filter(
                    Todo.user_id == user_id,
                    Todo.completed == False,
                    Todo.due_date < now
                ).count()
                
                # 按优先级统计
                priority_stats = {}
                for priority in ['high', 'medium', 'low']:
                    count = session.query(Todo).filter(
                        Todo.user_id == user_id,
                        Todo.priority == priority,
                        Todo.completed == False
                    ).count()
                    priority_stats[priority] = count
                
                return {
                    'total_todos': total_todos,
                    'completed_todos': completed_todos,
                    'pending_todos': pending_todos,
                    'overdue_todos': overdue_todos,
                    'priority_stats': priority_stats,
                    'completion_rate': (completed_todos / total_todos * 100) if total_todos > 0 else 0
                }
                
        except Exception as e:
            print(f"获取待办事项统计失败: {e}")
            return {}
    
    def get_todo_summary(self, todo_id: int) -> Optional[Dict[str, Any]]:
        """
        获取待办事项摘要信息
        
        Args:
            todo_id: 待办事项ID
            
        Returns:
            待办事项摘要字典或None
        """
        todo = self.get_todo(todo_id)
        if not todo:
            return None
        
        return {
            'id': todo.id,
            'user_id': todo.user_id,
            'title': todo.title,
            'description': todo.description,
            'completed': getattr(todo, 'completed', False),
            'priority': getattr(todo, 'priority', 'medium'),
            'status': todo.get_status_display(),
            'due_date': todo.due_date.isoformat() if hasattr(todo, 'due_date') and todo.due_date is not None else None,
            'note_id': getattr(todo, 'note_id', None),
            'created_at': todo.created_at.isoformat() if hasattr(todo, 'created_at') and todo.created_at is not None else None,
            'completed_at': todo.completed_at.isoformat() if hasattr(todo, 'completed_at') and todo.completed_at is not None else None
        }
    
    def close(self):
        """关闭数据库连接"""
        if self.db_client:
            self.db_client.close() 