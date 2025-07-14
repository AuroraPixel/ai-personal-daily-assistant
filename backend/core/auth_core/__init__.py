"""
认证核心模块

提供认证、授权、API响应等功能的统一入口
"""

# 认证相关
from .auth import (
    AuthUtils,
    AuthService,
    Token,
    TokenData,
    UserClaims,
    auth_service,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_DAYS
)

# 中间件相关
from .middleware import (
    AuthenticationError,
    PermissionError,
    get_token_from_request,
    get_current_user,
    get_current_user_optional,
    verify_user_permission,
    require_permission,
    CurrentUser,
    CurrentUserOptional
)

# API响应相关
from .api_response import (
    ErrorCode,
    ApiResponse,
    PaginatedApiResponse,
    BusinessException,
    ResponseBuilder,
    JsonResponseBuilder,
    success_response,
    error_response,
    invalid_credentials_response,
    unauthorized_response,
    not_found_response,
    validation_error_response,
    internal_error_response
)

__all__ = [
    # 认证
    "AuthUtils",
    "AuthService", 
    "Token",
    "TokenData",
    "UserClaims",
    "auth_service",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM", 
    "JWT_ACCESS_TOKEN_EXPIRE_DAYS",
    
    # 中间件
    "AuthenticationError",
    "PermissionError",
    "get_token_from_request",
    "get_current_user",
    "get_current_user_optional", 
    "verify_user_permission",
    "require_permission",
    "CurrentUser",
    "CurrentUserOptional",
    
    # API响应
    "ErrorCode",
    "ApiResponse",
    "PaginatedApiResponse", 
    "BusinessException",
    "ResponseBuilder",
    "JsonResponseBuilder",
    "success_response",
    "error_response",
    "invalid_credentials_response",
    "unauthorized_response",
    "not_found_response",
    "validation_error_response",
    "internal_error_response"
] 