"""
JSONPlaceholder API Data Models

Author: Andrew Wang
"""

from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class Address:
    """Address information"""
    street: str
    suite: str
    city: str
    zipcode: str
    geo: Dict[str, str]  # lat, lng


@dataclass
class Company:
    """Company information"""
    name: str
    catchPhrase: str
    bs: str


@dataclass
class User:
    """User information"""
    id: int
    name: str
    username: str
    email: str
    phone: str
    website: str
    address: Address
    company: Company


@dataclass
class Post:
    """Post information"""
    id: int
    userId: int
    title: str
    body: str


@dataclass
class Comment:
    """Comment information"""
    id: int
    postId: int
    name: str
    email: str
    body: str


@dataclass
class Album:
    """Album information"""
    id: int
    userId: int
    title: str


@dataclass
class Photo:
    """Photo information"""
    id: int
    albumId: int
    title: str
    url: str
    thumbnailUrl: str


@dataclass
class Todo:
    """Todo item information"""
    id: int
    userId: int
    title: str
    completed: bool


def address_from_dict(data: Dict) -> Address:
    """Create Address object from dictionary"""
    return Address(
        street=data["street"],
        suite=data["suite"],
        city=data["city"],
        zipcode=data["zipcode"],
        geo=data["geo"]
    )


def company_from_dict(data: Dict) -> Company:
    """Create Company object from dictionary"""
    return Company(
        name=data["name"],
        catchPhrase=data["catchPhrase"],
        bs=data["bs"]
    )


def user_from_dict(data: Dict) -> User:
    """Create User object from dictionary"""
    return User(
        id=data["id"],
        name=data["name"],
        username=data["username"],
        email=data["email"],
        phone=data["phone"],
        website=data["website"],
        address=address_from_dict(data["address"]),
        company=company_from_dict(data["company"])
    )


def post_from_dict(data: Dict) -> Post:
    """Create Post object from dictionary"""
    return Post(
        id=data["id"],
        userId=data["userId"],
        title=data["title"],
        body=data["body"]
    )


def comment_from_dict(data: Dict) -> Comment:
    """Create Comment object from dictionary"""
    return Comment(
        id=data["id"],
        postId=data["postId"],
        name=data["name"],
        email=data["email"],
        body=data["body"]
    )


def album_from_dict(data: Dict) -> Album:
    """Create Album object from dictionary"""
    return Album(
        id=data["id"],
        userId=data["userId"],
        title=data["title"]
    )


def photo_from_dict(data: Dict) -> Photo:
    """Create Photo object from dictionary"""
    return Photo(
        id=data["id"],
        albumId=data["albumId"],
        title=data["title"],
        url=data["url"],
        thumbnailUrl=data["thumbnailUrl"]
    )


def todo_from_dict(data: Dict) -> Todo:
    """Create Todo object from dictionary"""
    return Todo(
        id=data["id"],
        userId=data["userId"],
        title=data["title"],
        completed=data["completed"]
    )


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


def format_album(album: Album) -> str:
    """Format album information"""
    return f"""
Album Information:
ID: {album.id}
User ID: {album.userId}
Title: {album.title}
    """.strip()


def format_photo(photo: Photo) -> str:
    """Format photo information"""
    return f"""
Photo Information:
ID: {photo.id}
Album ID: {photo.albumId}
Title: {photo.title}
URL: {photo.url}
Thumbnail: {photo.thumbnailUrl}
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
    return f"[{post.id}] {post.title} (User: {post.userId})"


def format_comment_summary(comment: Comment) -> str:
    """Format comment summary"""
    return f"[{comment.id}] {comment.name} - {comment.email}"


def format_album_summary(album: Album) -> str:
    """Format album summary"""
    return f"[{album.id}] {album.title} (User: {album.userId})"


def format_photo_summary(photo: Photo) -> str:
    """Format photo summary"""
    return f"[{photo.id}] {photo.title} (Album: {photo.albumId})"


def format_todo_summary(todo: Todo) -> str:
    """Format todo item summary"""
    status = "✓" if todo.completed else "○"
    return f"[{todo.id}] {status} {todo.title} (User: {todo.userId})" 