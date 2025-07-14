"""
认证核心模块

提供JWT令牌生成、验证和用户认证相关功能
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# JWT配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_DAYS = 7

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 安全方案
security = HTTPBearer()


class TokenData(BaseModel):
    """JWT令牌数据模型"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: Dict[str, Any]


class UserClaims(BaseModel):
    """用户声明模型"""
    user_id: str
    username: str
    email: str
    exp: int
    iat: int


class AuthUtils:
    """认证工具类"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码
            
        Returns:
            是否验证成功
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        获取密码哈希
        
        Args:
            password: 明文密码
            
        Returns:
            哈希密码
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            JWT令牌字符串
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        验证令牌
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            解码后的数据或None
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def decode_token(token: str) -> Optional[UserClaims]:
        """
        解码令牌
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            用户声明对象或None
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return UserClaims(**payload)
        except (JWTError, ValueError):
            return None
    
    @staticmethod
    def get_current_user_from_token(token: str) -> Optional[Dict[str, Any]]:
        """
        从令牌获取当前用户信息
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            用户信息字典或None
        """
        payload = AuthUtils.verify_token(token)
        if payload is None:
            return None
        
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        
        return {
            "user_id": user_id,
            "username": payload.get("username"),
            "email": payload.get("email")
        }
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        用户认证（优化版本，使用缓存）
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            用户信息字典或None
        """
        # 固定密码验证
        if password != "admin123456":
            return None
        
        # 使用全局服务管理器获取缓存的用户信息
        try:
            from core.service_manager import service_manager
            
            # 使用缓存的用户信息查找
            user_info = service_manager.get_user_cached(
                user_id=username,  # 使用用户名作为缓存key的一部分
                username=username
            )
            
            if user_info:
                return user_info
            
            # 如果缓存中没有找到，回退到原始方法
            from service.services.user_service import UserService
            user_service = UserService()
            
            # 尝试通过用户名查找用户
            users = user_service.search_users_by_name(username)
            if not users:
                # 如果按名称找不到，尝试按邮箱查找
                users = user_service.search_users_by_email(username)
            
            if not users:
                return None
            
            # 取第一个匹配的用户
            user = users[0]
            return {
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "name": user.name
            }
            
        except Exception as e:
            # 如果优化版本出错，回退到原始方法
            from service.services.user_service import UserService
            user_service = UserService()
            
            # 尝试通过用户名查找用户
            users = user_service.search_users_by_name(username)
            if not users:
                # 如果按名称找不到，尝试按邮箱查找
                users = user_service.search_users_by_email(username)
            
            if not users:
                return None
            
            # 取第一个匹配的用户
            user = users[0]
            return {
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "name": user.name
            }


class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.user_service = None
    
    def login(self, username: str, password: str) -> Optional[Token]:
        """
        用户登录
        
        Args:
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            令牌对象或None
        """
        # 认证用户
        user = AuthUtils.authenticate_user(username, password)
        if not user:
            return None
        
        # 创建令牌数据
        token_data = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"]
        }
        
        # 创建访问令牌
        access_token = AuthUtils.create_access_token(data=token_data)
        
        # 计算过期时间
        expires_in = int(timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS).total_seconds())
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            user_info=user
        )
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证令牌（优化版本，使用缓存）
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            用户信息字典或None
        """
        try:
            # 使用服务管理器的缓存验证
            from core.service_manager import service_manager
            return service_manager.verify_token_cached(token)
        except Exception:
            # 如果缓存验证失败，回退到原始方法
            return AuthUtils.get_current_user_from_token(token)
    
    def refresh_token(self, token: str) -> Optional[Token]:
        """
        刷新令牌
        
        Args:
            token: 当前令牌
            
        Returns:
            新的令牌对象或None
        """
        user = self.verify_token(token)
        if not user:
            return None
        
        # 重新生成令牌
        token_data = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"]
        }
        
        access_token = AuthUtils.create_access_token(data=token_data)
        expires_in = int(timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS).total_seconds())
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            user_info=user
        )


# 全局认证服务实例
auth_service = AuthService() 