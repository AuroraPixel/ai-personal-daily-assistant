"""
JSONPlaceholder API数据模型
"""

from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class Address:
    """地址信息"""
    street: str
    suite: str
    city: str
    zipcode: str
    geo: Dict[str, str]  # lat, lng


@dataclass
class Company:
    """公司信息"""
    name: str
    catchPhrase: str
    bs: str


@dataclass
class User:
    """用户信息"""
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
    """帖子信息"""
    id: int
    userId: int
    title: str
    body: str


@dataclass
class Comment:
    """评论信息"""
    id: int
    postId: int
    name: str
    email: str
    body: str


@dataclass
class Album:
    """相册信息"""
    id: int
    userId: int
    title: str


@dataclass
class Photo:
    """照片信息"""
    id: int
    albumId: int
    title: str
    url: str
    thumbnailUrl: str


@dataclass
class Todo:
    """待办事项信息"""
    id: int
    userId: int
    title: str
    completed: bool


def address_from_dict(data: Dict) -> Address:
    """从字典创建Address对象"""
    return Address(
        street=data["street"],
        suite=data["suite"],
        city=data["city"],
        zipcode=data["zipcode"],
        geo=data["geo"]
    )


def company_from_dict(data: Dict) -> Company:
    """从字典创建Company对象"""
    return Company(
        name=data["name"],
        catchPhrase=data["catchPhrase"],
        bs=data["bs"]
    )


def user_from_dict(data: Dict) -> User:
    """从字典创建User对象"""
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
    """从字典创建Post对象"""
    return Post(
        id=data["id"],
        userId=data["userId"],
        title=data["title"],
        body=data["body"]
    )


def comment_from_dict(data: Dict) -> Comment:
    """从字典创建Comment对象"""
    return Comment(
        id=data["id"],
        postId=data["postId"],
        name=data["name"],
        email=data["email"],
        body=data["body"]
    )


def album_from_dict(data: Dict) -> Album:
    """从字典创建Album对象"""
    return Album(
        id=data["id"],
        userId=data["userId"],
        title=data["title"]
    )


def photo_from_dict(data: Dict) -> Photo:
    """从字典创建Photo对象"""
    return Photo(
        id=data["id"],
        albumId=data["albumId"],
        title=data["title"],
        url=data["url"],
        thumbnailUrl=data["thumbnailUrl"]
    )


def todo_from_dict(data: Dict) -> Todo:
    """从字典创建Todo对象"""
    return Todo(
        id=data["id"],
        userId=data["userId"],
        title=data["title"],
        completed=data["completed"]
    )


def format_user(user: User) -> str:
    """格式化用户信息"""
    return f"""
用户信息:
ID: {user.id}
姓名: {user.name} ({user.username})
邮箱: {user.email}
电话: {user.phone}
网站: {user.website}
地址: {user.address.street} {user.address.suite}, {user.address.city} {user.address.zipcode}
公司: {user.company.name} - {user.company.catchPhrase}
    """.strip()


def format_post(post: Post) -> str:
    """格式化帖子信息"""
    return f"""
帖子信息:
ID: {post.id}
用户ID: {post.userId}
标题: {post.title}
内容: {post.body}
    """.strip()


def format_comment(comment: Comment) -> str:
    """格式化评论信息"""
    return f"""
评论信息:
ID: {comment.id}
帖子ID: {comment.postId}
姓名: {comment.name}
邮箱: {comment.email}
内容: {comment.body}
    """.strip()


def format_album(album: Album) -> str:
    """格式化相册信息"""
    return f"""
相册信息:
ID: {album.id}
用户ID: {album.userId}
标题: {album.title}
    """.strip()


def format_photo(photo: Photo) -> str:
    """格式化照片信息"""
    return f"""
照片信息:
ID: {photo.id}
相册ID: {photo.albumId}
标题: {photo.title}
URL: {photo.url}
缩略图: {photo.thumbnailUrl}
    """.strip()


def format_todo(todo: Todo) -> str:
    """格式化待办事项信息"""
    status = "已完成" if todo.completed else "未完成"
    return f"""
待办事项:
ID: {todo.id}
用户ID: {todo.userId}
标题: {todo.title}
状态: {status}
    """.strip()


def format_user_summary(user: User) -> str:
    """格式化用户摘要"""
    return f"{user.name} ({user.username}) - {user.email}"


def format_post_summary(post: Post) -> str:
    """格式化帖子摘要"""
    return f"[{post.id}] {post.title} (用户: {post.userId})"


def format_comment_summary(comment: Comment) -> str:
    """格式化评论摘要"""
    return f"[{comment.id}] {comment.name} - {comment.email}"


def format_album_summary(album: Album) -> str:
    """格式化相册摘要"""
    return f"[{album.id}] {album.title} (用户: {album.userId})"


def format_photo_summary(photo: Photo) -> str:
    """格式化照片摘要"""
    return f"[{photo.id}] {photo.title} (相册: {photo.albumId})"


def format_todo_summary(todo: Todo) -> str:
    """格式化待办事项摘要"""
    status = "✓" if todo.completed else "○"
    return f"[{todo.id}] {status} {todo.title} (用户: {todo.userId})" 