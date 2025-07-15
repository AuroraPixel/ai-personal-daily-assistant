"""
笔记API模块

包含笔记创建、更新、删除、查询等笔记相关的API端点
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Path, Query, Body
from pydantic import BaseModel, Field

# 导入认证核心模块
from core.auth_core import CurrentUser

# 导入服务管理器
from service.service_manager import service_manager

# 导入服务类
from service.services.note_service import NoteService

# 配置日志
logger = logging.getLogger(__name__)

# 创建笔记API路由器
note_router = APIRouter(prefix="/notes", tags=["笔记"])

# =========================
# 数据模型
# =========================

class NoteCreateRequest(BaseModel):
    """创建笔记请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="笔记标题")
    content: str = Field(default="", max_length=10000, description="笔记内容")
    tag: Optional[str] = Field(default=None, description="笔记标签")
    status: str = Field(default="draft", description="笔记状态")


class NoteUpdateRequest(BaseModel):
    """更新笔记请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="笔记标题")
    content: Optional[str] = Field(None, max_length=10000, description="笔记内容")
    tag: Optional[str] = Field(None, description="笔记标签")
    status: Optional[str] = Field(None, description="笔记状态")


class NoteResponse(BaseModel):
    """笔记响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class NoteListResponse(BaseModel):
    """笔记列表响应模型"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    total: int = 0
    user_id: int


class NoteSearchResponse(BaseModel):
    """笔记搜索响应模型"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    search_query: str
    total: int = 0
    user_id: int


# =========================
# API端点
# =========================

@note_router.post("/{user_id}")
async def create_note(
    user_id: int = Path(..., description="用户ID"),
    request: NoteCreateRequest = Body(..., description="创建笔记请求"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    创建新笔记
    
    Args:
        user_id: 用户ID
        request: 创建笔记请求
        current_user: 当前认证用户
        
    Returns:
        创建笔记响应
    """
    try:
        # 验证用户只能创建自己的笔记
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权为其他用户创建笔记")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 创建笔记
        note = note_service.create_note(
            user_id=user_id,
            title=request.title,
            content=request.content,
            tag=request.tag,
            status=request.status
        )
        
        if not note:
            raise HTTPException(status_code=400, detail="创建笔记失败")
        
        # 转换为响应格式
        note_data = {
            "id": note.id,
            "user_id": note.user_id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "status": note.status,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "updated_at": note.updated_at.isoformat() if note.updated_at else None,
            "last_updated": note.last_updated.isoformat() if note.last_updated else None
        }
        
        return NoteResponse(
            success=True,
            message="笔记创建成功",
            data=note_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建笔记失败: {str(e)}")


@note_router.get("/{user_id}")
async def get_user_notes(
    user_id: int = Path(..., description="用户ID"),
    tag: Optional[str] = Query(None, description="标签过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取用户的笔记列表
    
    Args:
        user_id: 用户ID
        tag: 标签过滤
        status: 状态过滤
        search: 搜索关键词
        limit: 返回数量限制
        offset: 偏移量
        current_user: 当前认证用户
        
    Returns:
        笔记列表响应
    """
    try:
        # 验证用户只能访问自己的笔记
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问其他用户的笔记")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 获取用户笔记列表
        notes = note_service.get_user_notes(
            user_id=user_id,
            tag=tag,
            status=status,
            search_query=search,
            limit=limit,
            offset=offset
        )
        
        # 转换为响应格式
        notes_data = []
        for note in notes:
            note_data = {
                "id": note.id,
                "user_id": note.user_id,
                "title": note.title,
                "content": note.content,
                "tag": note.tag,
                "status": note.status,
                "created_at": note.created_at.isoformat() if note.created_at else None,
                "updated_at": note.updated_at.isoformat() if note.updated_at else None,
                "last_updated": note.last_updated.isoformat() if note.last_updated else None
            }
            notes_data.append(note_data)
        
        return NoteListResponse(
            success=True,
            message=f"成功获取用户 {user_id} 的笔记列表",
            data=notes_data,
            total=len(notes_data),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户笔记列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取笔记列表失败: {str(e)}")


@note_router.get("/{user_id}/{note_id}")
async def get_note(
    user_id: int = Path(..., description="用户ID"),
    note_id: int = Path(..., description="笔记ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取单个笔记详情
    
    Args:
        user_id: 用户ID
        note_id: 笔记ID
        current_user: 当前认证用户
        
    Returns:
        笔记详情响应
    """
    try:
        # 验证用户只能访问自己的笔记
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问其他用户的笔记")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 获取笔记
        note = note_service.get_note(note_id)
        
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在")
        
        # 验证笔记属于当前用户
        if note.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权访问此笔记")
        
        # 转换为响应格式
        note_data = {
            "id": note.id,
            "user_id": note.user_id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "status": note.status,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "updated_at": note.updated_at.isoformat() if note.updated_at else None,
            "last_updated": note.last_updated.isoformat() if note.last_updated else None
        }
        
        return NoteResponse(
            success=True,
            message="成功获取笔记详情",
            data=note_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取笔记详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取笔记详情失败: {str(e)}")


@note_router.put("/{user_id}/{note_id}")
async def update_note(
    user_id: int = Path(..., description="用户ID"),
    note_id: int = Path(..., description="笔记ID"),
    request: NoteUpdateRequest = Body(..., description="更新笔记请求"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    更新笔记
    
    Args:
        user_id: 用户ID
        note_id: 笔记ID
        request: 更新笔记请求
        current_user: 当前认证用户
        
    Returns:
        更新笔记响应
    """
    try:
        # 验证用户只能更新自己的笔记
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权更新其他用户的笔记")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 先获取笔记验证存在性和权限
        note = note_service.get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在")
        
        if note.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权更新此笔记")
        
        # 准备更新数据
        update_data = {}
        if request.title is not None:
            update_data['title'] = request.title
        if request.content is not None:
            update_data['content'] = request.content
        if request.tag is not None:
            update_data['tag'] = request.tag
        if request.status is not None:
            update_data['status'] = request.status
        
        # 更新笔记
        updated_note = note_service.update_note(note_id, **update_data)
        
        if not updated_note:
            raise HTTPException(status_code=400, detail="更新笔记失败")
        
        # 转换为响应格式
        note_data = {
            "id": updated_note.id,
            "user_id": updated_note.user_id,
            "title": updated_note.title,
            "content": updated_note.content,
            "tag": updated_note.tag,
            "status": updated_note.status,
            "created_at": updated_note.created_at.isoformat() if updated_note.created_at else None,
            "updated_at": updated_note.updated_at.isoformat() if updated_note.updated_at else None,
            "last_updated": updated_note.last_updated.isoformat() if updated_note.last_updated else None
        }
        
        return NoteResponse(
            success=True,
            message="笔记更新成功",
            data=note_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新笔记失败: {str(e)}")


@note_router.delete("/{user_id}/{note_id}")
async def delete_note(
    user_id: int = Path(..., description="用户ID"),
    note_id: int = Path(..., description="笔记ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    删除笔记
    
    Args:
        user_id: 用户ID
        note_id: 笔记ID
        current_user: 当前认证用户
        
    Returns:
        删除笔记响应
    """
    try:
        # 验证用户只能删除自己的笔记
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权删除其他用户的笔记")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 先获取笔记验证存在性和权限
        note = note_service.get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在")
        
        if note.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权删除此笔记")
        
        # 删除笔记
        success = note_service.delete_note(note_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="删除笔记失败")
        
        return NoteResponse(
            success=True,
            message="笔记删除成功",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除笔记失败: {str(e)}")


@note_router.post("/{user_id}/search")
async def search_notes(
    user_id: int = Path(..., description="用户ID"),
    search_query: str = Body(..., embed=True, description="搜索查询"),
    tag: Optional[str] = Query(None, description="标签过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    搜索笔记（向量搜索）
    
    Args:
        user_id: 用户ID
        search_query: 搜索查询
        tag: 标签过滤
        status: 状态过滤
        limit: 返回数量限制
        current_user: 当前认证用户
        
    Returns:
        搜索结果响应
    """
    try:
        # 验证用户只能搜索自己的笔记
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权搜索其他用户的笔记")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 搜索笔记
        results = note_service.search_notes(
            user_id=user_id,
            query=search_query,
            tag=tag,
            status=status,
            limit=limit
        )
        
        # 转换为响应格式
        notes_data = []
        for result in results:
            note_data = {
                "id": result.get("id"),
                "user_id": result.get("user_id"),
                "title": result.get("title"),
                "content": result.get("content"),
                "tag": result.get("tag"),
                "status": result.get("status"),
                "created_at": result.get("created_at"),
                "updated_at": result.get("updated_at"),
                "last_updated": result.get("last_updated"),
                "similarity_score": result.get("similarity_score", 0.0)
            }
            notes_data.append(note_data)
        
        return NoteSearchResponse(
            success=True,
            message=f"成功搜索用户 {user_id} 的笔记",
            data=notes_data,
            search_query=search_query,
            total=len(notes_data),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索笔记失败: {str(e)}")


@note_router.get("/{user_id}/tags")
async def get_note_tags(
    user_id: int = Path(..., description="用户ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取用户笔记的所有标签
    
    Args:
        user_id: 用户ID
        current_user: 当前认证用户
        
    Returns:
        标签列表响应
    """
    try:
        # 验证用户只能访问自己的笔记标签
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问其他用户的笔记标签")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 获取用户笔记标签
        tags = note_service.get_user_tags(user_id)
        
        return NoteResponse(
            success=True,
            message=f"成功获取用户 {user_id} 的笔记标签",
            data={"tags": tags}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取笔记标签失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取笔记标签失败: {str(e)}") 