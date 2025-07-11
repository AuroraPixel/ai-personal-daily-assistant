"""
JSONPlaceholder API Client

Author: Andrew Wang
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
    """JSONPlaceholder API Client"""
    
    def __init__(self):
        self.client = APIClient("https://jsonplaceholder.typicode.com")
    
    # User related methods
    def get_users(self) -> Optional[List[User]]:
        """Get all users"""
        data = self.client.get("/users")
        if data:
            return [user_from_dict(user_data) for user_data in data]
        return None
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get specified user"""
        data = self.client.get(f"/users/{user_id}")
        if data:
            return user_from_dict(data)
        return None
    
    # Post related methods
    def get_posts(self, user_id: Optional[int] = None) -> Optional[List[Post]]:
        """Get post list"""
        endpoint = "/posts"
        params = {}
        if user_id:
            params["userId"] = user_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [post_from_dict(post_data) for post_data in data]
        return None
    
    def get_post(self, post_id: int) -> Optional[Post]:
        """Get specified post"""
        data = self.client.get(f"/posts/{post_id}")
        if data:
            return post_from_dict(data)
        return None
    
    def get_user_posts(self, user_id: int) -> Optional[List[Post]]:
        """Get user's posts"""
        return self.get_posts(user_id=user_id)
    
    # Comment related methods
    def get_comments(self, post_id: Optional[int] = None) -> Optional[List[Comment]]:
        """Get comment list"""
        endpoint = "/comments"
        params = {}
        if post_id:
            params["postId"] = post_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [comment_from_dict(comment_data) for comment_data in data]
        return None
    
    def get_comment(self, comment_id: int) -> Optional[Comment]:
        """Get specified comment"""
        data = self.client.get(f"/comments/{comment_id}")
        if data:
            return comment_from_dict(data)
        return None
    
    def get_post_comments(self, post_id: int) -> Optional[List[Comment]]:
        """Get post's comments"""
        return self.get_comments(post_id=post_id)
    
    # Album related methods
    def get_albums(self, user_id: Optional[int] = None) -> Optional[List[Album]]:
        """Get album list"""
        endpoint = "/albums"
        params = {}
        if user_id:
            params["userId"] = user_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [album_from_dict(album_data) for album_data in data]
        return None
    
    def get_album(self, album_id: int) -> Optional[Album]:
        """Get specified album"""
        data = self.client.get(f"/albums/{album_id}")
        if data:
            return album_from_dict(data)
        return None
    
    def get_user_albums(self, user_id: int) -> Optional[List[Album]]:
        """Get user's albums"""
        return self.get_albums(user_id=user_id)
    
    # Photo related methods
    def get_photos(self, album_id: Optional[int] = None) -> Optional[List[Photo]]:
        """Get photo list"""
        endpoint = "/photos"
        params = {}
        if album_id:
            params["albumId"] = album_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [photo_from_dict(photo_data) for photo_data in data]
        return None
    
    def get_photo(self, photo_id: int) -> Optional[Photo]:
        """Get specified photo"""
        data = self.client.get(f"/photos/{photo_id}")
        if data:
            return photo_from_dict(data)
        return None
    
    def get_album_photos(self, album_id: int) -> Optional[List[Photo]]:
        """Get album's photos"""
        return self.get_photos(album_id=album_id)
    
    # Todo related methods
    def get_todos(self, user_id: Optional[int] = None) -> Optional[List[Todo]]:
        """Get todo list"""
        endpoint = "/todos"
        params = {}
        if user_id:
            params["userId"] = user_id
        
        data = self.client.get(endpoint, params=params)
        if data:
            return [todo_from_dict(todo_data) for todo_data in data]
        return None
    
    def get_todo(self, todo_id: int) -> Optional[Todo]:
        """Get specified todo"""
        data = self.client.get(f"/todos/{todo_id}")
        if data:
            return todo_from_dict(data)
        return None
    
    def get_user_todos(self, user_id: int) -> Optional[List[Todo]]:
        """Get user's todos"""
        return self.get_todos(user_id=user_id)
    
    def get_completed_todos(self, user_id: Optional[int] = None) -> Optional[List[Todo]]:
        """Get completed todos"""
        todos = self.get_todos(user_id=user_id)
        if todos:
            return [todo for todo in todos if todo.completed]
        return None
    
    def get_pending_todos(self, user_id: Optional[int] = None) -> Optional[List[Todo]]:
        """Get pending todos"""
        todos = self.get_todos(user_id=user_id)
        if todos:
            return [todo for todo in todos if not todo.completed]
        return None
    
    # Format methods
    def format_users_list(self, users: List[User], max_items: int = 10) -> str:
        """Format user list"""
        if not users:
            return "No users found"
        
        formatted = []
        for i, user in enumerate(users[:max_items]):
            formatted.append(f"{i+1}. {format_user_summary(user)}")
        
        if len(users) > max_items:
            formatted.append(f"... {len(users) - max_items} more users")
        
        return "\n".join(formatted)
    
    def format_posts_list(self, posts: List[Post], max_items: int = 10) -> str:
        """Format post list"""
        if not posts:
            return "No posts found"
        
        formatted = []
        for i, post in enumerate(posts[:max_items]):
            formatted.append(f"{i+1}. {format_post_summary(post)}")
        
        if len(posts) > max_items:
            formatted.append(f"... {len(posts) - max_items} more posts")
        
        return "\n".join(formatted)
    
    def format_comments_list(self, comments: List[Comment], max_items: int = 10) -> str:
        """Format comment list"""
        if not comments:
            return "No comments found"
        
        formatted = []
        for i, comment in enumerate(comments[:max_items]):
            formatted.append(f"{i+1}. {format_comment_summary(comment)}")
        
        if len(comments) > max_items:
            formatted.append(f"... {len(comments) - max_items} more comments")
        
        return "\n".join(formatted)
    
    def format_albums_list(self, albums: List[Album], max_items: int = 10) -> str:
        """Format album list"""
        if not albums:
            return "No albums found"
        
        formatted = []
        for i, album in enumerate(albums[:max_items]):
            formatted.append(f"{i+1}. {format_album_summary(album)}")
        
        if len(albums) > max_items:
            formatted.append(f"... {len(albums) - max_items} more albums")
        
        return "\n".join(formatted)
    
    def format_photos_list(self, photos: List[Photo], max_items: int = 10) -> str:
        """Format photo list"""
        if not photos:
            return "No photos found"
        
        formatted = []
        for i, photo in enumerate(photos[:max_items]):
            formatted.append(f"{i+1}. {format_photo_summary(photo)}")
        
        if len(photos) > max_items:
            formatted.append(f"... {len(photos) - max_items} more photos")
        
        return "\n".join(formatted)
    
    def format_todos_list(self, todos: List[Todo], max_items: int = 10) -> str:
        """Format todo list"""
        if not todos:
            return "No todos found"
        
        formatted = []
        for i, todo in enumerate(todos[:max_items]):
            formatted.append(f"{i+1}. {format_todo_summary(todo)}")
        
        if len(todos) > max_items:
            formatted.append(f"... {len(todos) - max_items} more todos")
        
        return "\n".join(formatted)
    
    # Comprehensive query methods
    def get_user_summary(self, user_id: int) -> str:
        """Get user's complete summary"""
        user = self.get_user(user_id)
        if not user:
            return f"User {user_id} not found"
        
        summary = [format_user(user)]
        
        # Get user's posts
        posts = self.get_user_posts(user_id)
        if posts:
            summary.append(f"\nPosts: {len(posts)}")
            summary.append(self.format_posts_list(posts, max_items=3))
        
        # Get user's albums
        albums = self.get_user_albums(user_id)
        if albums:
            summary.append(f"\nAlbums: {len(albums)}")
            summary.append(self.format_albums_list(albums, max_items=3))
        
        # Get user's todos
        todos = self.get_user_todos(user_id)
        if todos:
            completed_count = len([t for t in todos if t.completed])
            pending_count = len([t for t in todos if not t.completed])
            summary.append(f"\nTodos: {completed_count} completed, {pending_count} pending")
            summary.append(self.format_todos_list(todos, max_items=5))
        
        return "\n".join(summary)
    
    def get_post_details(self, post_id: int) -> str:
        """Get post's detailed information"""
        post = self.get_post(post_id)
        if not post:
            return f"Post {post_id} not found"
        
        details = [format_post(post)]
        
        # Get post's comments
        comments = self.get_post_comments(post_id)
        if comments:
            details.append(f"\nComments: {len(comments)}")
            details.append(self.format_comments_list(comments, max_items=5))
        
        return "\n".join(details) 