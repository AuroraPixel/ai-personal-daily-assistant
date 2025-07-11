"""
JSONPlaceholder API Client

Author: Andrew Wang
"""

import json
from typing import Optional, List
from core.http_core.client import APIClient
from .models import (
    User, Post, Comment, Todo,
    UsersApiResponse, UserApiResponse, PostsApiResponse, CommentsApiResponse, TodosApiResponse,
    format_user, format_post, format_comment, format_todo,
    format_user_summary, format_post_summary, format_comment_summary, format_todo_summary
)


class JSONPlaceholderClient:
    """JSONPlaceholder API Client"""
    
    def __init__(self):
        self.client = APIClient("https://jsonplaceholder.typicode.com")
    
    def get_users(self) -> Optional[UsersApiResponse]:
        """Get all users"""
        data = self.client.get("/users")
        if data and isinstance(data, list):
            return UsersApiResponse.from_list(data)
        return None
    
    def get_user(self, user_id: int) -> Optional[UserApiResponse]:
        """Get specific user by ID"""
        data = self.client.get(f"/users/{user_id}")
        if data:
            return UserApiResponse.from_dict(data)
        return None
    
    def get_user_posts(self, user_id: int) -> Optional[PostsApiResponse]:
        """Get user's posts"""
        data = self.client.get(f"/users/{user_id}/posts")
        if data and isinstance(data, list):
            return PostsApiResponse.from_list(data)
        return None
    
    def get_user_comments(self, user_id: int) -> Optional[CommentsApiResponse]:
        """Get user's comments (comments on posts by the user)"""
        # First get all posts by this user
        posts_data = self.client.get(f"/users/{user_id}/posts")
        if not posts_data or not isinstance(posts_data, list):
            return None
            
        # Then get comments for each post
        all_comments = []
        for post in posts_data:
            post_id = post["id"]
            comments_data = self.client.get(f"/posts/{post_id}/comments")
            if comments_data and isinstance(comments_data, list):
                all_comments.extend(comments_data)
        
        if all_comments:
            return CommentsApiResponse.from_list(all_comments)
        return None
    
    def get_post_comments(self, post_id: int) -> Optional[CommentsApiResponse]:
        """Get post's comments"""
        data = self.client.get(f"/posts/{post_id}/comments")
        if data and isinstance(data, list):
            return CommentsApiResponse.from_list(data)
        return None
    
    def get_user_todos(self, user_id: int) -> Optional[TodosApiResponse]:
        """Get user's todos"""
        data = self.client.get(f"/users/{user_id}/todos")
        if data and isinstance(data, list):
            return TodosApiResponse.from_list(data)
        return None
    
    def format_users_list(self, users_response: UsersApiResponse, max_items: int = 10) -> str:
        """Format users list"""
        if not users_response.users:
            return "No users found"
        
        formatted = []
        for i, user in enumerate(users_response.users[:max_items]):
            formatted.append(f"{i+1}. {format_user_summary(user)}")
        
        if len(users_response.users) > max_items:
            formatted.append(f"... {len(users_response.users) - max_items} more users")
        
        return "\n".join(formatted)
    
    def format_posts_list(self, posts_response: PostsApiResponse, max_items: int = 10) -> str:
        """Format posts list"""
        if not posts_response.posts:
            return "No posts found"
        
        formatted = []
        for i, post in enumerate(posts_response.posts[:max_items]):
            formatted.append(f"{i+1}. {format_post_summary(post)}")
        
        if len(posts_response.posts) > max_items:
            formatted.append(f"... {len(posts_response.posts) - max_items} more posts")
        
        return "\n".join(formatted)
    
    def format_comments_list(self, comments_response: CommentsApiResponse, max_items: int = 10) -> str:
        """Format comments list"""
        if not comments_response.comments:
            return "No comments found"
        
        formatted = []
        for i, comment in enumerate(comments_response.comments[:max_items]):
            formatted.append(f"{i+1}. {format_comment_summary(comment)}")
        
        if len(comments_response.comments) > max_items:
            formatted.append(f"... {len(comments_response.comments) - max_items} more comments")
        
        return "\n".join(formatted)
    
    def format_todos_list(self, todos_response: TodosApiResponse, max_items: int = 10) -> str:
        """Format todos list"""
        if not todos_response.todos:
            return "No todos found"
        
        formatted = []
        for i, todo in enumerate(todos_response.todos[:max_items]):
            formatted.append(f"{i+1}. {format_todo_summary(todo)}")
        
        if len(todos_response.todos) > max_items:
            formatted.append(f"... {len(todos_response.todos) - max_items} more todos")
        
        return "\n".join(formatted)
    
    def get_user_details(self, user_id: int) -> str:
        """Get user details"""
        user_response = self.get_user(user_id)
        if user_response:
            return format_user(user_response.user)
        return f"User {user_id} not found" 