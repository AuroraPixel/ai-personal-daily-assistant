"""
JSONPlaceholder API客户端
"""

from typing import Optional, List
from core.http_core.client import APIClient
from .models import (
    User, Post, Comment, Album, Photo, Todo,
    user_from_dict, post_from_dict, comment_from_dict,
    album_from_dict, photo_from_dict, todo_from_dict,
    format_user, format_post, format_comment, format_album, format_photo, format_todo,
    format_user_summary, format_post_summary, format_comment_summary,
    format_album_summary, format_photo_summary, format_todo_summary
)


class JSONPlaceholderClient:
    """JSONPlaceholder API客户端"""
    
    def __init__(self):
        self.client = APIClient("https://jsonplaceholder.typicode.com")
    
    # 用户相关方法
    def get_users(self) -> Optional[List[User]]:
        """获取所有用户"""
        data = self.client.get("/users")
        if data:
            return [user_from_dict(user_data) for user_data in data]
        return None
    
    def get_user(self, user_id: int) -> Optional[User]:
        """获取指定用户"""
        data = self.client.get(f"/users/{user_id}")
        if data:
            return user_from_dict(data)
        return None
    
    # 帖子相关方法
    def get_posts(self, user_id: Optional[int] = None) -> Optional[List[Post]]:
        """获取帖子列表"""
        endpoint = "/posts"
        params = {}
        if user_id:
            params["userId"] = user_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [post_from_dict(post_data) for post_data in data]
        return None
    
    def get_post(self, post_id: int) -> Optional[Post]:
        """获取指定帖子"""
        data = self.client.get(f"/posts/{post_id}")
        if data:
            return post_from_dict(data)
        return None
    
    def get_user_posts(self, user_id: int) -> Optional[List[Post]]:
        """获取用户的帖子"""
        return self.get_posts(user_id=user_id)
    
    # 评论相关方法
    def get_comments(self, post_id: Optional[int] = None) -> Optional[List[Comment]]:
        """获取评论列表"""
        endpoint = "/comments"
        params = {}
        if post_id:
            params["postId"] = post_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [comment_from_dict(comment_data) for comment_data in data]
        return None
    
    def get_comment(self, comment_id: int) -> Optional[Comment]:
        """获取指定评论"""
        data = self.client.get(f"/comments/{comment_id}")
        if data:
            return comment_from_dict(data)
        return None
    
    def get_post_comments(self, post_id: int) -> Optional[List[Comment]]:
        """获取帖子的评论"""
        return self.get_comments(post_id=post_id)
    
    # 相册相关方法
    def get_albums(self, user_id: Optional[int] = None) -> Optional[List[Album]]:
        """获取相册列表"""
        endpoint = "/albums"
        params = {}
        if user_id:
            params["userId"] = user_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [album_from_dict(album_data) for album_data in data]
        return None
    
    def get_album(self, album_id: int) -> Optional[Album]:
        """获取指定相册"""
        data = self.client.get(f"/albums/{album_id}")
        if data:
            return album_from_dict(data)
        return None
    
    def get_user_albums(self, user_id: int) -> Optional[List[Album]]:
        """获取用户的相册"""
        return self.get_albums(user_id=user_id)
    
    # 照片相关方法
    def get_photos(self, album_id: Optional[int] = None) -> Optional[List[Photo]]:
        """获取照片列表"""
        endpoint = "/photos"
        params = {}
        if album_id:
            params["albumId"] = album_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [photo_from_dict(photo_data) for photo_data in data]
        return None
    
    def get_photo(self, photo_id: int) -> Optional[Photo]:
        """获取指定照片"""
        data = self.client.get(f"/photos/{photo_id}")
        if data:
            return photo_from_dict(data)
        return None
    
    def get_album_photos(self, album_id: int) -> Optional[List[Photo]]:
        """获取相册的照片"""
        return self.get_photos(album_id=album_id)
    
    # 待办事项相关方法
    def get_todos(self, user_id: Optional[int] = None) -> Optional[List[Todo]]:
        """获取待办事项列表"""
        endpoint = "/todos"
        params = {}
        if user_id:
            params["userId"] = user_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [todo_from_dict(todo_data) for todo_data in data]
        return None
    
    def get_todo(self, todo_id: int) -> Optional[Todo]:
        """获取指定待办事项"""
        data = self.client.get(f"/todos/{todo_id}")
        if data:
            return todo_from_dict(data)
        return None
    
    def get_user_todos(self, user_id: int) -> Optional[List[Todo]]:
        """获取用户的待办事项"""
        return self.get_todos(user_id=user_id)
    
    def get_completed_todos(self, user_id: Optional[int] = None) -> Optional[List[Todo]]:
        """获取已完成的待办事项"""
        todos = self.get_todos(user_id=user_id)
        if todos:
            return [todo for todo in todos if todo.completed]
        return None
    
    def get_pending_todos(self, user_id: Optional[int] = None) -> Optional[List[Todo]]:
        """获取未完成的待办事项"""
        todos = self.get_todos(user_id=user_id)
        if todos:
            return [todo for todo in todos if not todo.completed]
        return None
    
    # 格式化方法
    def format_users_list(self, users: List[User], max_items: int = 10) -> str:
        """格式化用户列表"""
        if not users:
            return "没有找到用户"
        
        formatted = []
        for i, user in enumerate(users[:max_items]):
            formatted.append(f"{i+1}. {format_user_summary(user)}")
        
        if len(users) > max_items:
            formatted.append(f"... 还有 {len(users) - max_items} 个用户")
        
        return "\n".join(formatted)
    
    def format_posts_list(self, posts: List[Post], max_items: int = 10) -> str:
        """格式化帖子列表"""
        if not posts:
            return "没有找到帖子"
        
        formatted = []
        for i, post in enumerate(posts[:max_items]):
            formatted.append(f"{i+1}. {format_post_summary(post)}")
        
        if len(posts) > max_items:
            formatted.append(f"... 还有 {len(posts) - max_items} 个帖子")
        
        return "\n".join(formatted)
    
    def format_comments_list(self, comments: List[Comment], max_items: int = 10) -> str:
        """格式化评论列表"""
        if not comments:
            return "没有找到评论"
        
        formatted = []
        for i, comment in enumerate(comments[:max_items]):
            formatted.append(f"{i+1}. {format_comment_summary(comment)}")
        
        if len(comments) > max_items:
            formatted.append(f"... 还有 {len(comments) - max_items} 个评论")
        
        return "\n".join(formatted)
    
    def format_albums_list(self, albums: List[Album], max_items: int = 10) -> str:
        """格式化相册列表"""
        if not albums:
            return "没有找到相册"
        
        formatted = []
        for i, album in enumerate(albums[:max_items]):
            formatted.append(f"{i+1}. {format_album_summary(album)}")
        
        if len(albums) > max_items:
            formatted.append(f"... 还有 {len(albums) - max_items} 个相册")
        
        return "\n".join(formatted)
    
    def format_photos_list(self, photos: List[Photo], max_items: int = 10) -> str:
        """格式化照片列表"""
        if not photos:
            return "没有找到照片"
        
        formatted = []
        for i, photo in enumerate(photos[:max_items]):
            formatted.append(f"{i+1}. {format_photo_summary(photo)}")
        
        if len(photos) > max_items:
            formatted.append(f"... 还有 {len(photos) - max_items} 张照片")
        
        return "\n".join(formatted)
    
    def format_todos_list(self, todos: List[Todo], max_items: int = 10) -> str:
        """格式化待办事项列表"""
        if not todos:
            return "没有找到待办事项"
        
        formatted = []
        for i, todo in enumerate(todos[:max_items]):
            formatted.append(f"{i+1}. {format_todo_summary(todo)}")
        
        if len(todos) > max_items:
            formatted.append(f"... 还有 {len(todos) - max_items} 个待办事项")
        
        return "\n".join(formatted)
    
    # 综合查询方法
    def get_user_summary(self, user_id: int) -> str:
        """获取用户的完整摘要"""
        user = self.get_user(user_id)
        if not user:
            return f"未找到用户 {user_id}"
        
        summary = [format_user(user)]
        
        # 获取用户的帖子
        posts = self.get_user_posts(user_id)
        if posts:
            summary.append(f"\n帖子数量: {len(posts)}")
            summary.append(self.format_posts_list(posts, max_items=3))
        
        # 获取用户的相册
        albums = self.get_user_albums(user_id)
        if albums:
            summary.append(f"\n相册数量: {len(albums)}")
            summary.append(self.format_albums_list(albums, max_items=3))
        
        # 获取用户的待办事项
        todos = self.get_user_todos(user_id)
        if todos:
            completed_count = len([t for t in todos if t.completed])
            pending_count = len([t for t in todos if not t.completed])
            summary.append(f"\n待办事项: {completed_count} 已完成, {pending_count} 未完成")
            summary.append(self.format_todos_list(todos, max_items=5))
        
        return "\n".join(summary)
    
    def get_post_details(self, post_id: int) -> str:
        """获取帖子的详细信息"""
        post = self.get_post(post_id)
        if not post:
            return f"未找到帖子 {post_id}"
        
        details = [format_post(post)]
        
        # 获取帖子的评论
        comments = self.get_post_comments(post_id)
        if comments:
            details.append(f"\n评论数量: {len(comments)}")
            details.append(self.format_comments_list(comments, max_items=5))
        
        return "\n".join(details) 