"""
用户服务

整合JSONPlaceholder API用户数据，提供用户相关业务逻辑
"""

from typing import Optional, List
from remote_api.jsonplaceholder.client import JSONPlaceholderClient
from remote_api.jsonplaceholder.models import User


class UserService:
    """
    用户服务类
    
    提供用户相关的业务逻辑，用户数据来自JSONPlaceholder API
    """
    
    def __init__(self):
        """初始化用户服务"""
        self.client = JSONPlaceholderClient()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息或None
        """
        try:
            user_response = self.client.get_user(user_id)
            if user_response:
                return user_response.user
            return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def get_all_users(self) -> List[User]:
        """
        获取所有用户信息
        
        Returns:
            用户列表
        """
        try:
            users_response = self.client.get_users()
            if users_response:
                return users_response.users
            return []
        except Exception as e:
            print(f"获取所有用户失败: {e}")
            return []
    
    def get_user_posts(self, user_id: int):
        """
        获取用户的帖子
        
        Args:
            user_id: 用户ID
            
        Returns:
            帖子列表
        """
        try:
            posts_response = self.client.get_user_posts(user_id)
            if posts_response:
                return posts_response.posts
            return []
        except Exception as e:
            print(f"获取用户帖子失败: {e}")
            return []
    
    def get_user_todos(self, user_id: int):
        """
        获取用户的待办事项（JSONPlaceholder API）
        
        Args:
            user_id: 用户ID
            
        Returns:
            待办事项列表
        """
        try:
            todos_response = self.client.get_user_todos(user_id)
            if todos_response:
                return todos_response.todos
            return []
        except Exception as e:
            print(f"获取用户待办事项失败: {e}")
            return []
    
    def validate_user_exists(self, user_id: int) -> bool:
        """
        验证用户是否存在
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否存在
        """
        user = self.get_user(user_id)
        return user is not None
    
    def get_user_display_name(self, user_id: int) -> str:
        """
        获取用户显示名称
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户显示名称
        """
        user = self.get_user(user_id)
        if user:
            return user.name
        return f"用户 {user_id}"
    
    def get_user_email(self, user_id: int) -> Optional[str]:
        """
        获取用户邮箱
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户邮箱或None
        """
        user = self.get_user(user_id)
        if user:
            return user.email
        return None
    
    def search_users_by_name(self, name: str) -> List[User]:
        """
        根据姓名搜索用户
        
        Args:
            name: 搜索的姓名
            
        Returns:
            匹配的用户列表
        """
        all_users = self.get_all_users()
        return [
            user for user in all_users 
            if name.lower() in user.name.lower()
        ]
    
    def search_users_by_email(self, email: str) -> List[User]:
        """
        根据邮箱搜索用户
        
        Args:
            email: 搜索的邮箱
            
        Returns:
            匹配的用户列表
        """
        all_users = self.get_all_users()
        return [
            user for user in all_users 
            if email.lower() in user.email.lower()
        ]
    
    def get_user_summary(self, user_id: int) -> dict:
        """
        获取用户概要信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户概要信息字典
        """
        user = self.get_user(user_id)
        if not user:
            return {}
        
        return {
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'website': user.website,
            'company': user.company.name if user.company else None,
            'address': {
                'city': user.address.city if user.address else None,
                'zipcode': user.address.zipcode if user.address else None
            }
        } 