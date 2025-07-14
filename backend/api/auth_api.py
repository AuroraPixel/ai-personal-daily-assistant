"""
认证API模块

包含用户登录、登出、令牌刷新等认证相关的API端点
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

# 导入认证核心模块
from core.auth_core import (
    auth_service, 
    Token,
    CurrentUser, 
    CurrentUserOptional,
    success_response,
    invalid_credentials_response,
    internal_error_response
)

# 配置日志
logger = logging.getLogger(__name__)

# 创建认证API路由器
auth_router = APIRouter(prefix="/api/auth", tags=["认证"])

# =========================
# 数据模型
# =========================

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应模型"""
    success: bool
    message: str
    token: Optional[Token] = None
    user_info: Optional[Dict[str, Any]] = None


class LogoutResponse(BaseModel):
    """退出登录响应模型"""
    success: bool
    message: str

# =========================
# API端点
# =========================

@auth_router.post("/login")
async def login(response: Response, login_request: LoginRequest):
    """
    用户登录接口
    
    Args:
        response: FastAPI响应对象
        login_request: 登录请求数据
        
    Returns:
        统一API响应格式
    """
    try:
        # 验证用户凭据
        token = auth_service.login(login_request.username, login_request.password)
        
        if not token:
            # 用户名或密码错误，返回401状态码
            return invalid_credentials_response("用户名或密码错误")
        
        # 设置Cookie
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            max_age=token.expires_in,
            httponly=True,
            secure=False,  # 在生产环境中应该设置为True
            samesite="lax"
        )
        
        logger.info(f"用户 {login_request.username} 登录成功")
        
        # 构建成功响应数据
        response_data = {
            "access_token": token.access_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in,
            "user_info": token.user_info
        }
        
        return success_response(response_data, "登录成功")
        
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return internal_error_response("服务器内部错误")


@auth_router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response, current_user: Dict[str, Any] = CurrentUserOptional):
    """
    用户退出登录接口
    
    Args:
        response: FastAPI响应对象
        current_user: 当前用户信息（可选）
        
    Returns:
        退出登录响应
    """
    try:
        # 清除Cookie
        response.delete_cookie(key="access_token")
        
        username = current_user.get("username", "未知用户") if current_user else "未知用户"
        logger.info(f"用户 {username} 退出登录")
        
        return LogoutResponse(
            success=True,
            message="退出登录成功"
        )
        
    except Exception as e:
        logger.error(f"退出登录失败: {str(e)}")
        return LogoutResponse(
            success=False,
            message=f"退出登录失败: {str(e)}"
        )


@auth_router.post("/refresh", response_model=LoginResponse)
async def refresh_token(response: Response, current_user: Dict[str, Any] = CurrentUser):
    """
    刷新令牌接口
    
    Args:
        response: FastAPI响应对象
        current_user: 当前用户信息
        
    Returns:
        新的令牌信息
    """
    try:
        # 重新生成令牌
        token_data = {
            "user_id": current_user["user_id"],
            "username": current_user["username"],
            "email": current_user["email"]
        }
        
        new_token = auth_service.login(current_user["username"], "admin123456")
        
        if not new_token:
            raise HTTPException(status_code=401, detail="令牌刷新失败")
        
        # 更新Cookie
        response.set_cookie(
            key="access_token",
            value=new_token.access_token,
            max_age=new_token.expires_in,
            httponly=True,
            secure=False,  # 在生产环境中应该设置为True
            samesite="lax"
        )
        
        logger.info(f"用户 {current_user['username']} 刷新令牌成功")
        
        return LoginResponse(
            success=True,
            message="令牌刷新成功",
            token=new_token,
            user_info=new_token.user_info
        )
        
    except Exception as e:
        logger.error(f"令牌刷新失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"令牌刷新失败: {str(e)}")


@auth_router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = CurrentUser):
    """
    获取当前用户信息接口
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        用户信息
    """
    return {
        "success": True,
        "message": "获取用户信息成功",
        "user_info": current_user
    } 