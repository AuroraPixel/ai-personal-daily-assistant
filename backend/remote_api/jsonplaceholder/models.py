"""
JSONPlaceholder API Data Models

Author: Andrew Wang
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


class GeoLocation(BaseModel):
    """Geographical location coordinates"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    lat: str        # Latitude coordinate
    lng: str        # Longitude coordinate


class Address(BaseModel):
    """User address information"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    street: str         # Street address
    suite: str          # Suite/apartment number
    city: str           # City name
    zipcode: str        # Postal/ZIP code
    geo: GeoLocation    # Geographical coordinates


class Company(BaseModel):
    """User company information"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    name: str           # Company name
    catchPhrase: str    # Company catch phrase/slogan
    bs: str             # Company business description


class User(BaseModel):
    """User profile information"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    id: int                 # User unique identifier
    name: str               # User full name
    username: str           # User login username
    email: str              # User email address
    phone: str              # User phone number
    website: str            # User personal website
    address: Address        # User address information
    company: Company        # User company information


class Post(BaseModel):
    """Blog post information"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    id: int         # Post unique identifier
    userId: int     # Author user ID
    title: str      # Post title/headline
    body: str       # Post content/body text


class Comment(BaseModel):
    """Comment on a post"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    id: int         # Comment unique identifier
    postId: int     # Parent post ID
    name: str       # Comment title/subject
    email: str      # Commenter email address
    body: str       # Comment content/body text


class Todo(BaseModel):
    """Todo item/task"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    id: int             # Todo unique identifier
    userId: int         # Owner user ID
    title: str          # Todo item title/description
    completed: bool     # Completion status (true=completed, false=pending)


class UsersApiResponse(BaseModel):
    """API response for users list"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    users: List[User]       # List of users

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "UsersApiResponse":
        """Create UsersApiResponse from list of dictionaries"""
        users = [User(**user_data) for user_data in data]
        return cls(users=users)


class UserApiResponse(BaseModel):
    """API response for single user"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    user: User              # Single user object

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserApiResponse":
        """Create UserApiResponse from dictionary"""
        user = User(**data)
        return cls(user=user)


class PostsApiResponse(BaseModel):
    """API response for posts list"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    posts: List[Post]       # List of posts

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "PostsApiResponse":
        """Create PostsApiResponse from list of dictionaries"""
        posts = [Post(**post_data) for post_data in data]
        return cls(posts=posts)


class CommentsApiResponse(BaseModel):
    """API response for comments list"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    comments: List[Comment]     # List of comments

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "CommentsApiResponse":
        """Create CommentsApiResponse from list of dictionaries"""
        comments = [Comment(**comment_data) for comment_data in data]
        return cls(comments=comments)


class TodosApiResponse(BaseModel):
    """API response for todos list"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    todos: List[Todo]       # List of todos

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "TodosApiResponse":
        """Create TodosApiResponse from list of dictionaries"""
        todos = [Todo(**todo_data) for todo_data in data]
        return cls(todos=todos)


def format_user(user: User) -> str:
    """Format user information"""
    return f"""
User Information:
ID: {user.id}
Name: {user.name} ({user.username})
Email: {user.email}
Phone: {user.phone}
Website: {user.website}
Address: {user.address.street} {user.address.suite}, {user.address.city} {user.address.zipcode}
Company: {user.company.name} - {user.company.catchPhrase}
    """.strip()


def format_post(post: Post) -> str:
    """Format post information"""
    return f"""
Post Information:
ID: {post.id}
User ID: {post.userId}
Title: {post.title}
Content: {post.body}
    """.strip()


def format_comment(comment: Comment) -> str:
    """Format comment information"""
    return f"""
Comment Information:
ID: {comment.id}
Post ID: {comment.postId}
Name: {comment.name}
Email: {comment.email}
Content: {comment.body}
    """.strip()


def format_todo(todo: Todo) -> str:
    """Format todo item information"""
    status = "Completed" if todo.completed else "Pending"
    return f"""
Todo Item:
ID: {todo.id}
User ID: {todo.userId}
Title: {todo.title}
Status: {status}
    """.strip()


def format_user_summary(user: User) -> str:
    """Format user summary"""
    return f"{user.name} ({user.username}) - {user.email}"


def format_post_summary(post: Post) -> str:
    """Format post summary"""
    return f"Post #{post.id}: {post.title}"


def format_comment_summary(comment: Comment) -> str:
    """Format comment summary"""
    return f"Comment #{comment.id}: {comment.name} - {comment.email}"


def format_todo_summary(todo: Todo) -> str:
    """Format todo summary"""
    status = "✓" if todo.completed else "○"
    return f"Todo #{todo.id}: {status} {todo.title}" 