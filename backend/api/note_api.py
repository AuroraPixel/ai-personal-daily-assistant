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
from core.auth_core import CurrentUser, success_response, error_response, not_found_response, validation_error_response, internal_error_response

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





class NoteSearchRequest(BaseModel):
    """搜索笔记请求模型"""
    query: str = Field(..., min_length=1, description="搜索查询")
    use_vector_search: bool = Field(default=True, description="是否使用向量搜索")
    tag: Optional[str] = Field(default=None, description="标签过滤")
    status: Optional[str] = Field(default=None, description="状态过滤")
    limit: Optional[int] = Field(default=10, ge=1, le=50, description="返回数量限制")


# =========================
# API端点 - 按照路由具体性排序
# =========================

@note_router.post("/{user_id}/search")
async def search_notes(
    user_id: int = Path(..., description="用户ID"),
    request: NoteSearchRequest = Body(..., description="搜索笔记请求"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    搜索笔记（支持向量搜索）
    
    Args:
        user_id: 用户ID
        request: 搜索笔记请求
        current_user: 当前认证用户
        
    Returns:
        搜索笔记响应
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
        
        search_results = []
        
        # 向量搜索（如果有查询词）
        if request.query and request.use_vector_search:
            try:
                vector_results = note_service.search_notes_by_vector(
                    user_id=user_id,
                    query=request.query,
                    limit=request.limit or 10
                )
                
                # 转换向量搜索结果
                for result in vector_results:
                    search_results.append({
                        "id": result.get("id"),
                        "user_id": user_id,
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "tag": result.get("tag", ""),
                        "status": result.get("status", "draft"),
                        "created_at": result.get("created_at", ""),
                        "updated_at": result.get("updated_at", ""),
                        "last_updated": result.get("last_updated", ""),
                        "similarity_score": result.get("similarity_score", 0.0),
                        "search_type": "vector"
                    })
                    
            except Exception as e:
                logger.warning(f"向量搜索失败，回退到文本搜索: {e}")
                # 回退到普通搜索
                request.use_vector_search = False
        
        # 普通文本搜索（如果没有向量搜索或作为回退）
        if not request.use_vector_search and request.query:
            notes = note_service.search_notes(
                user_id=user_id,
                query=request.query,
                search_in_content=True,
                search_in_tags=True,
                tag=request.tag,
                status=request.status,
                limit=request.limit or 20
            )
            
            # 转换普通搜索结果
            for note in notes:
                search_results.append({
                    "id": note.id,
                    "user_id": note.user_id,
                    "title": note.title,
                    "content": note.content,
                    "tag": note.tag,
                    "status": note.status,
                    "created_at": note.created_at.isoformat() if note.created_at else None,
                    "updated_at": note.updated_at.isoformat() if note.updated_at else None,
                    "last_updated": note.last_updated.isoformat() if note.last_updated else None,
                    "similarity_score": 1.0,  # 文本搜索没有相似度分数
                    "search_type": "text"
                })
        
        response_data = {
            "data": search_results,
            "total": len(search_results),
            "user_id": user_id,
            "query": request.query,
            "search_type": "vector" if request.use_vector_search else "text"
        }
        
        return success_response(response_data, f"搜索完成，找到 {len(search_results)} 条结果")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索笔记失败: {str(e)}")
        return internal_error_response(f"搜索笔记失败: {str(e)}")


@note_router.get("/{user_id}/tags")
async def get_user_note_tags(
    user_id: int = Path(..., description="用户ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取用户的所有笔记标签
    
    Args:
        user_id: 用户ID
        current_user: 当前认证用户
        
    Returns:
        标签列表响应
    """
    try:
        # 验证用户只能访问自己的笔记标签
        if str(user_id) != current_user["user_id"]:
            return internal_error_response("无权访问其他用户的笔记标签")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 获取标签列表
        tags = note_service.get_user_tags(user_id)
        
        response_data = {
            "data": tags,
            "total": len(tags),
            "user_id": user_id
        }
        
        return success_response(response_data, f"成功获取用户 {user_id} 的笔记标签")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户笔记标签失败: {str(e)}")
        return internal_error_response(f"获取笔记标签失败: {str(e)}")


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
            return internal_error_response("无权为其他用户创建笔记")
        
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
            return internal_error_response("创建笔记失败")
        
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
        
        return success_response(note_data, "笔记创建成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建笔记失败: {str(e)}")
        return internal_error_response(f"创建笔记失败: {str(e)}")


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
            return internal_error_response("无权访问其他用户的笔记")
        
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
        
        response_data = {
            "data": notes_data,
            "total": len(notes_data),
            "user_id": user_id
        }
        
        return success_response(response_data, f"成功获取用户 {user_id} 的笔记列表")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户笔记列表失败: {str(e)}")
        return internal_error_response(f"获取笔记列表失败: {str(e)}")


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
            return internal_error_response("无权访问其他用户的笔记")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 获取笔记
        note = note_service.get_note(note_id)
        
        if not note:
            return not_found_response("笔记不存在")
        
        # 验证笔记属于当前用户
        if note.user_id != user_id:
            return internal_error_response("无权访问此笔记")
        
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
        
        return success_response(note_data, "成功获取笔记详情")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取笔记详情失败: {str(e)}")
        return internal_error_response(f"获取笔记详情失败: {str(e)}")


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
            return internal_error_response("无权更新其他用户的笔记")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 先获取笔记验证存在性和权限
        note = note_service.get_note(note_id)
        if not note:
            return not_found_response("笔记不存在")
        
        if note.user_id != user_id:
            return internal_error_response("无权更新此笔记")
        
        # 更新笔记
        updated_note = note_service.update_note(
            note_id=note_id,
            title=request.title,
            content=request.content,
            tag=request.tag,
            status=request.status
        )
        
        if not updated_note:
            return internal_error_response("更新笔记失败")
        
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
        
        return success_response(note_data, "笔记更新成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新笔记失败: {str(e)}")
        return internal_error_response(f"更新笔记失败: {str(e)}")


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
            return internal_error_response("无权删除其他用户的笔记")
        
        # 使用服务管理器获取笔记服务
        note_service = service_manager.get_service(
            'note_service',
            NoteService
        )
        
        # 先获取笔记验证存在性和权限
        note = note_service.get_note(note_id)
        if not note:
            return not_found_response("笔记不存在")
        
        if note.user_id != user_id:
            return internal_error_response("无权删除此笔记")
        
        # 删除笔记
        success = note_service.delete_note(note_id)
        
        if not success:
            return internal_error_response("删除笔记失败")
        
        return success_response(None, "笔记删除成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除笔记失败: {str(e)}")
        return internal_error_response(f"删除笔记失败: {str(e)}") 