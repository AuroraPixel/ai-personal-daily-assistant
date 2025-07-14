"""
统一API响应格式和错误处理
"""

from typing import Any, Optional, Dict, Union
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# 标准错误码定义
class ErrorCode:
    # 成功
    SUCCESS = 0
    
    # 客户端错误 (4xx)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    VALIDATION_ERROR = 422
    
    # 服务器错误 (5xx)
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503
    
    # 业务错误码 (自定义)
    AUTH_FAILED = 1001              # 认证失败
    INVALID_CREDENTIALS = 1002      # 用户名或密码错误
    TOKEN_EXPIRED = 1003            # 令牌过期
    TOKEN_INVALID = 1004            # 令牌无效
    USER_NOT_FOUND = 1005           # 用户不存在
    PERMISSION_DENIED = 1006        # 权限不足
    
    # 数据相关错误
    RESOURCE_NOT_FOUND = 2001       # 资源不存在
    RESOURCE_ALREADY_EXISTS = 2002  # 资源已存在
    DATA_VALIDATION_ERROR = 2003    # 数据验证错误
    
    # 外部服务错误
    EXTERNAL_SERVICE_ERROR = 3001   # 外部服务错误
    DATABASE_ERROR = 3002           # 数据库错误
    NETWORK_ERROR = 3003            # 网络错误

# 错误码对应的HTTP状态码映射
ERROR_CODE_TO_HTTP_STATUS = {
    ErrorCode.SUCCESS: 200,
    ErrorCode.BAD_REQUEST: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.METHOD_NOT_ALLOWED: 405,
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
    
    # 业务错误码默认映射
    ErrorCode.AUTH_FAILED: 401,
    ErrorCode.INVALID_CREDENTIALS: 200,  # 登录失败返回200+业务错误码，避免触发路由守卫
    ErrorCode.TOKEN_EXPIRED: 401,
    ErrorCode.TOKEN_INVALID: 401,
    ErrorCode.USER_NOT_FOUND: 404,
    ErrorCode.PERMISSION_DENIED: 403,
    
    ErrorCode.RESOURCE_NOT_FOUND: 404,
    ErrorCode.RESOURCE_ALREADY_EXISTS: 409,
    ErrorCode.DATA_VALIDATION_ERROR: 422,
    
    ErrorCode.EXTERNAL_SERVICE_ERROR: 502,
    ErrorCode.DATABASE_ERROR: 500,
    ErrorCode.NETWORK_ERROR: 502,
}

# 统一API响应模型
class ApiResponse(BaseModel):
    """统一API响应格式"""
    success: bool
    code: int
    message: str
    data: Optional[Any] = None
    timestamp: Optional[str] = None
    request_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            # 确保datetime等类型正确序列化
        }

# 分页响应模型
class PaginatedApiResponse(BaseModel):
    """分页API响应格式"""
    success: bool
    code: int
    message: str
    data: Optional[Any] = None
    pagination: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    request_id: Optional[str] = None

# 业务异常类
class BusinessException(Exception):
    """业务异常"""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

# API响应构建器
class ResponseBuilder:
    """API响应构建器"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = ErrorCode.SUCCESS) -> Dict[str, Any]:
        """构建成功响应"""
        return {
            "success": True,
            "code": code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """构建错误响应"""
        return {
            "success": False,
            "code": code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def paginated_success(
        data: Any, 
        total: int, 
        page: int, 
        size: int, 
        message: str = "获取成功",
        code: int = ErrorCode.SUCCESS
    ) -> Dict[str, Any]:
        """构建分页成功响应"""
        return {
            "success": True,
            "code": code,
            "message": message,
            "data": data,
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "has_more": len(data) == size if isinstance(data, list) else False
            }
        }

# JSON响应构建器
class JsonResponseBuilder:
    """JSON响应构建器"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = ErrorCode.SUCCESS) -> JSONResponse:
        """构建成功JSON响应"""
        content = ResponseBuilder.success(data, message, code)
        http_status = ERROR_CODE_TO_HTTP_STATUS.get(code, 200)
        return JSONResponse(content=content, status_code=http_status)
    
    @staticmethod
    def error(code: int, message: str, data: Any = None) -> JSONResponse:
        """构建错误JSON响应"""
        content = ResponseBuilder.error(code, message, data)
        http_status = ERROR_CODE_TO_HTTP_STATUS.get(code, 500)
        return JSONResponse(content=content, status_code=http_status)
    
    @staticmethod
    def business_error(exception: BusinessException) -> JSONResponse:
        """构建业务异常JSON响应"""
        return JsonResponseBuilder.error(exception.code, exception.message, exception.data)

# 常用响应快捷方法
def success_response(data: Any = None, message: str = "操作成功") -> JSONResponse:
    """成功响应快捷方法"""
    return JsonResponseBuilder.success(data, message)

def error_response(code: int, message: str, data: Any = None) -> JSONResponse:
    """错误响应快捷方法"""
    return JsonResponseBuilder.error(code, message, data)

def invalid_credentials_response(message: str = "用户名或密码错误") -> JSONResponse:
    """用户名密码错误响应"""
    return JsonResponseBuilder.error(ErrorCode.INVALID_CREDENTIALS, message)

def unauthorized_response(message: str = "未授权访问") -> JSONResponse:
    """未授权响应"""
    return JsonResponseBuilder.error(ErrorCode.UNAUTHORIZED, message)

def not_found_response(message: str = "资源不存在") -> JSONResponse:
    """资源不存在响应"""
    return JsonResponseBuilder.error(ErrorCode.NOT_FOUND, message)

def validation_error_response(message: str = "数据验证失败") -> JSONResponse:
    """数据验证错误响应"""
    return JsonResponseBuilder.error(ErrorCode.DATA_VALIDATION_ERROR, message)

def internal_error_response(message: str = "服务器内部错误") -> JSONResponse:
    """服务器内部错误响应"""
    return JsonResponseBuilder.error(ErrorCode.INTERNAL_ERROR, message) 