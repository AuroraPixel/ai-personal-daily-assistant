"""
认证中间件模块

提供FastAPI的认证中间件和依赖注入装饰器
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth import AuthUtils, auth_service

# HTTP Bearer 安全方案
security = HTTPBearer(auto_error=False)


class AuthenticationError(HTTPException):
    """认证错误异常"""
    def __init__(self, detail: str = "认证失败"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionError(HTTPException):
    """权限错误异常"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def get_token_from_request(request: Request, 
                          credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
                          access_token: Optional[str] = Cookie(None)) -> Optional[str]:
    """
    从请求中获取JWT令牌
    
    优先级：
    1. Authorization头
    2. Cookie中的access_token
    3. 查询参数中的token
    
    Args:
        request: FastAPI请求对象
        credentials: HTTP Bearer认证凭据
        access_token: Cookie中的令牌
        
    Returns:
        JWT令牌字符串或None
    """
    # 1. 从Authorization头获取
    if credentials and credentials.credentials:
        return credentials.credentials
    
    # 2. 从Cookie获取
    if access_token:
        return access_token
    
    # 3. 从查询参数获取 (主要用于WebSocket)
    token = request.query_params.get("token")
    if token:
        return token
    
    return None


def get_current_user(request: Request, 
                    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
                    access_token: Optional[str] = Cookie(None)) -> Dict[str, Any]:
    """
    获取当前用户信息（必需认证）
    
    Args:
        request: FastAPI请求对象
        credentials: HTTP Bearer认证凭据
        access_token: Cookie中的令牌
        
    Returns:
        用户信息字典
        
    Raises:
        AuthenticationError: 认证失败
    """
    token = get_token_from_request(request, credentials, access_token)
    
    if not token:
        raise AuthenticationError("缺少认证令牌")
    
    user = auth_service.verify_token(token)
    if not user:
        raise AuthenticationError("无效的认证令牌")
    
    return user


def get_current_user_optional(request: Request, 
                             credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
                             access_token: Optional[str] = Cookie(None)) -> Optional[Dict[str, Any]]:
    """
    获取当前用户信息（可选认证）
    
    Args:
        request: FastAPI请求对象
        credentials: HTTP Bearer认证凭据
        access_token: Cookie中的令牌
        
    Returns:
        用户信息字典或None
    """
    token = get_token_from_request(request, credentials, access_token)
    
    if not token:
        return None
    
    user = auth_service.verify_token(token)
    return user


def verify_user_permission(user: Dict[str, Any], required_permission: Optional[str] = None) -> bool:
    """
    验证用户权限
    
    Args:
        user: 用户信息
        required_permission: 所需权限
        
    Returns:
        是否有权限
    """
    # 目前所有认证用户都有权限
    # 可以在这里添加更复杂的权限验证逻辑
    return True


def require_permission(permission: Optional[str] = None):
    """
    权限验证装饰器
    
    Args:
        permission: 所需权限
        
    Returns:
        依赖注入函数
    """
    def permission_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if not verify_user_permission(user, permission):
            raise PermissionError(f"需要权限: {permission}")
        return user
    
    return permission_checker


# 预定义的依赖注入装饰器
CurrentUser = Depends(get_current_user)
CurrentUserOptional = Depends(get_current_user_optional)
AdminUser = Depends(require_permission("admin")) 