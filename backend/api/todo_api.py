"""
待办事项API模块

包含待办事项创建、更新、删除、查询等待办事项相关的API端点
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
from service.services.todo_service import TodoService

# 配置日志
logger = logging.getLogger(__name__)

# 创建待办事项API路由器
todo_router = APIRouter(prefix="/todos", tags=["待办事项"])

# =========================
# 数据模型
# =========================

class TodoCreateRequest(BaseModel):
    """创建待办事项请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="待办事项标题")
    description: str = Field(default="", max_length=1000, description="待办事项描述")
    priority: str = Field(default="medium", description="优先级 (high, medium, low)")
    due_date: Optional[datetime] = Field(default=None, description="截止日期")
    note_id: Optional[int] = Field(default=None, description="关联的笔记ID")


class TodoUpdateRequest(BaseModel):
    """更新待办事项请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="待办事项标题")
    description: Optional[str] = Field(None, max_length=1000, description="待办事项描述")
    priority: Optional[str] = Field(None, description="优先级 (high, medium, low)")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    note_id: Optional[int] = Field(None, description="关联的笔记ID")
    completed: Optional[bool] = Field(None, description="完成状态")


class TodoResponse(BaseModel):
    """待办事项响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class TodoListResponse(BaseModel):
    """待办事项列表响应模型"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    total: int = 0
    user_id: int


class TodoStatsResponse(BaseModel):
    """待办事项统计响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    user_id: int


# =========================
# API端点 - 按照路由具体性排序
# =========================

@todo_router.get("/{user_id}/stats")
async def get_todo_stats(
    user_id: int = Path(..., description="用户ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取用户待办事项统计信息
    
    Args:
        user_id: 用户ID
        current_user: 当前认证用户
        
    Returns:
        待办事项统计响应
    """
    try:
        # 验证用户只能访问自己的待办事项统计
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问其他用户的待办事项统计")
        
        # 使用服务管理器获取待办事项服务
        todo_service = service_manager.get_service(
            'todo_service',
            TodoService
        )
        
        # 获取统计信息
        stats = todo_service.get_user_stats(user_id)
        
        return TodoStatsResponse(
            success=True,
            message=f"成功获取用户 {user_id} 的待办事项统计",
            data=stats,
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取待办事项统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取待办事项统计失败: {str(e)}")


@todo_router.get("/{user_id}/by-note/{note_id}")
async def get_todos_by_note(
    user_id: int = Path(..., description="用户ID"),
    note_id: int = Path(..., description="笔记ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取关联到特定笔记的待办事项
    
    Args:
        user_id: 用户ID
        note_id: 笔记ID
        current_user: 当前认证用户
        
    Returns:
        关联笔记的待办事项列表响应
    """
    try:
        # 验证用户只能访问自己的待办事项
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问其他用户的待办事项")
        
        # 使用服务管理器获取待办事项服务
        todo_service = service_manager.get_service(
            'todo_service',
            TodoService
        )
        
        # 获取关联笔记的待办事项
        todos = todo_service.get_todos_by_note(user_id, note_id)
        
        # 转换为响应格式
        todos_data = []
        for todo in todos:
            todo_data = {
                "id": todo.id,
                "user_id": todo.user_id,
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
                "priority": todo.priority,
                "note_id": todo.note_id,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
                "last_updated": todo.last_updated.isoformat() if todo.last_updated else None,
                "is_overdue": todo.is_overdue(),
                "status_display": todo.get_status_display()
            }
            todos_data.append(todo_data)
        
        return TodoListResponse(
            success=True,
            message=f"成功获取笔记 {note_id} 关联的待办事项",
            data=todos_data,
            total=len(todos_data),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取关联笔记的待办事项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取关联笔记的待办事项失败: {str(e)}")


@todo_router.post("/{user_id}/{todo_id}/complete")
async def complete_todo(
    user_id: int = Path(..., description="用户ID"),
    todo_id: int = Path(..., description="待办事项ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    标记待办事项为完成
    
    Args:
        user_id: 用户ID
        todo_id: 待办事项ID
        current_user: 当前认证用户
        
    Returns:
        完成待办事项响应
    """
    try:
        # 验证用户只能完成自己的待办事项
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权完成其他用户的待办事项")
        
        # 使用服务管理器获取待办事项服务
        todo_service = service_manager.get_service(
            'todo_service',
            TodoService
        )
        
        # 先获取待办事项验证存在性和权限
        todo = todo_service.get_todo(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="待办事项不存在")
        
        if todo.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权完成此待办事项")
        
        # 标记为完成
        success = todo_service.complete_todo(todo_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="完成待办事项失败")
        
        # 获取更新后的待办事项
        updated_todo = todo_service.get_todo(todo_id)
        
        # 转换为响应格式
        todo_data = {
            "id": updated_todo.id,
            "user_id": updated_todo.user_id,
            "title": updated_todo.title,
            "description": updated_todo.description,
            "completed": updated_todo.completed,
            "priority": updated_todo.priority,
            "note_id": updated_todo.note_id,
            "due_date": updated_todo.due_date.isoformat() if updated_todo.due_date else None,
            "completed_at": updated_todo.completed_at.isoformat() if updated_todo.completed_at else None,
            "created_at": updated_todo.created_at.isoformat() if updated_todo.created_at else None,
            "updated_at": updated_todo.updated_at.isoformat() if updated_todo.updated_at else None,
            "last_updated": updated_todo.last_updated.isoformat() if updated_todo.last_updated else None,
            "is_overdue": updated_todo.is_overdue(),
            "status_display": updated_todo.get_status_display()
        }
        
        return TodoResponse(
            success=True,
            message="待办事项已标记为完成",
            data=todo_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"完成待办事项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"完成待办事项失败: {str(e)}")


@todo_router.post("/{user_id}/{todo_id}/uncomplete")
async def uncomplete_todo(
    user_id: int = Path(..., description="用户ID"),
    todo_id: int = Path(..., description="待办事项ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    取消待办事项完成状态
    
    Args:
        user_id: 用户ID
        todo_id: 待办事项ID
        current_user: 当前认证用户
        
    Returns:
        取消完成待办事项响应
    """
    try:
        # 验证用户只能操作自己的待办事项
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权操作其他用户的待办事项")
        
        # 使用服务管理器获取待办事项服务
        todo_service = service_manager.get_service(
            'todo_service',
            TodoService
        )
        
        # 先获取待办事项验证存在性和权限
        todo = todo_service.get_todo(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="待办事项不存在")
        
        if todo.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权操作此待办事项")
        
        # 取消完成状态
        success = todo_service.uncomplete_todo(todo_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="取消完成状态失败")
        
        # 获取更新后的待办事项
        updated_todo = todo_service.get_todo(todo_id)
        
        # 转换为响应格式
        todo_data = {
            "id": updated_todo.id,
            "user_id": updated_todo.user_id,
            "title": updated_todo.title,
            "description": updated_todo.description,
            "completed": updated_todo.completed,
            "priority": updated_todo.priority,
            "note_id": updated_todo.note_id,
            "due_date": updated_todo.due_date.isoformat() if updated_todo.due_date else None,
            "completed_at": updated_todo.completed_at.isoformat() if updated_todo.completed_at else None,
            "created_at": updated_todo.created_at.isoformat() if updated_todo.created_at else None,
            "updated_at": updated_todo.updated_at.isoformat() if updated_todo.updated_at else None,
            "last_updated": updated_todo.last_updated.isoformat() if updated_todo.last_updated else None,
            "is_overdue": updated_todo.is_overdue(),
            "status_display": updated_todo.get_status_display()
        }
        
        return TodoResponse(
            success=True,
            message="待办事项完成状态已取消",
            data=todo_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消待办事项完成状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消待办事项完成状态失败: {str(e)}")


@todo_router.post("/{user_id}")
async def create_todo(
    user_id: int = Path(..., description="用户ID"),
    request: TodoCreateRequest = Body(..., description="创建待办事项请求"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    创建新待办事项
    
    Args:
        user_id: 用户ID
        request: 创建待办事项请求
        current_user: 当前认证用户
        
    Returns:
        创建待办事项响应
    """
    try:
        # 验证用户只能创建自己的待办事项
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权为其他用户创建待办事项")
        
        # 验证优先级
        if request.priority not in ['high', 'medium', 'low']:
            raise HTTPException(status_code=400, detail="优先级必须是 high, medium, low 之一")
        
        # 使用服务管理器获取待办事项服务
        todo_service = service_manager.get_service(
            'todo_service',
            TodoService
        )
        
        # 创建待办事项
        todo = todo_service.create_todo(
            user_id=user_id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            due_date=request.due_date,
            note_id=request.note_id
        )
        
        if not todo:
            raise HTTPException(status_code=400, detail="创建待办事项失败")
        
        # 转换为响应格式
        todo_data = {
            "id": todo.id,
            "user_id": todo.user_id,
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed,
            "priority": todo.priority,
            "note_id": todo.note_id,
            "due_date": todo.due_date.isoformat() if todo.due_date else None,
            "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
            "created_at": todo.created_at.isoformat() if todo.created_at else None,
            "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
            "last_updated": todo.last_updated.isoformat() if todo.last_updated else None
        }
        
        return TodoResponse(
            success=True,
            message="待办事项创建成功",
            data=todo_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建待办事项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建待办事项失败: {str(e)}")


@todo_router.get("/{user_id}")
async def get_user_todos(
    user_id: int = Path(..., description="用户ID"),
    completed: Optional[bool] = Query(None, description="完成状态过滤"),
    priority: Optional[str] = Query(None, description="优先级过滤"),
    overdue: Optional[bool] = Query(None, description="是否过期过滤"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取用户的待办事项列表
    
    Args:
        user_id: 用户ID
        completed: 完成状态过滤
        priority: 优先级过滤
        overdue: 是否过期过滤
        limit: 返回数量限制
        offset: 偏移量
        current_user: 当前认证用户
        
    Returns:
        待办事项列表响应
    """
    try:
        # 验证用户只能访问自己的待办事项
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问其他用户的待办事项")
        
        # 使用服务管理器获取待办事项服务
        todo_service = service_manager.get_service(
            'todo_service',
            TodoService
        )
        
        # 获取用户待办事项列表
        todos = todo_service.get_user_todos(
            user_id=user_id,
            completed=completed,
            priority=priority,
            limit=limit,
            offset=offset
        )
        
        # 转换为响应格式并处理过期过滤
        todos_data = []
        for todo in todos:
            # 检查是否过期
            is_overdue = todo.is_overdue()
            
            # 如果指定了过期过滤，则根据过期状态过滤
            if overdue is not None:
                if overdue and not is_overdue:
                    continue
                elif not overdue and is_overdue:
                    continue
            
            todo_data = {
                "id": todo.id,
                "user_id": todo.user_id,
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
                "priority": todo.priority,
                "note_id": todo.note_id,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
                "last_updated": todo.last_updated.isoformat() if todo.last_updated else None,
                "is_overdue": is_overdue,
                "status_display": todo.get_status_display()
            }
            todos_data.append(todo_data)
        
        return TodoListResponse(
            success=True,
            message=f"成功获取用户 {user_id} 的待办事项列表",
            data=todos_data,
            total=len(todos_data),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户待办事项列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取待办事项列表失败: {str(e)}")


@todo_router.get("/{user_id}/{todo_id}")
async def get_todo(
    user_id: int = Path(..., description="用户ID"),
    todo_id: int = Path(..., description="待办事项ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    获取单个待办事项详情
    
    Args:
        user_id: 用户ID
        todo_id: 待办事项ID
        current_user: 当前认证用户
        
    Returns:
        待办事项详情响应
    """
    try:
        # 验证用户只能访问自己的待办事项
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权访问其他用户的待办事项")
        
        # 使用服务管理器获取待办事项服务
        todo_service = service_manager.get_service(
            'todo_service',
            TodoService
        )
        
        # 获取待办事项
        todo = todo_service.get_todo(todo_id)
        
        if not todo:
            raise HTTPException(status_code=404, detail="待办事项不存在")
        
        # 验证待办事项属于当前用户
        if todo.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权访问此待办事项")
        
        # 转换为响应格式
        todo_data = {
            "id": todo.id,
            "user_id": todo.user_id,
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed,
            "priority": todo.priority,
            "note_id": todo.note_id,
            "due_date": todo.due_date.isoformat() if todo.due_date else None,
            "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
            "created_at": todo.created_at.isoformat() if todo.created_at else None,
            "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
            "last_updated": todo.last_updated.isoformat() if todo.last_updated else None,
            "is_overdue": todo.is_overdue(),
            "status_display": todo.get_status_display()
        }
        
        return TodoResponse(
            success=True,
            message="成功获取待办事项详情",
            data=todo_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取待办事项详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取待办事项详情失败: {str(e)}")


@todo_router.put("/{user_id}/{todo_id}")
async def update_todo(
    user_id: int = Path(..., description="用户ID"),
    todo_id: int = Path(..., description="待办事项ID"),
    request: TodoUpdateRequest = Body(..., description="更新待办事项请求"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    更新待办事项
    
    Args:
        user_id: 用户ID
        todo_id: 待办事项ID
        request: 更新待办事项请求
        current_user: 当前认证用户
        
    Returns:
        更新待办事项响应
    """
    try:
        # 验证用户只能更新自己的待办事项
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权更新其他用户的待办事项")
        
        # 验证优先级
        if request.priority is not None and request.priority not in ['high', 'medium', 'low']:
            raise HTTPException(status_code=400, detail="优先级必须是 high, medium, low 之一")
        
        # 使用服务管理器获取待办事项服务
        todo_service = service_manager.get_service(
            'todo_service',
            TodoService
        )
        
        # 先获取待办事项验证存在性和权限
        todo = todo_service.get_todo(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="待办事项不存在")
        
        if todo.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权更新此待办事项")
        
        # 准备更新数据
        update_data = {}
        if request.title is not None:
            update_data['title'] = request.title
        if request.description is not None:
            update_data['description'] = request.description
        if request.priority is not None:
            update_data['priority'] = request.priority
        if request.due_date is not None:
            update_data['due_date'] = request.due_date
        if request.note_id is not None:
            update_data['note_id'] = request.note_id
        
        # 更新待办事项
        success = todo_service.update_todo(todo_id, **update_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="更新待办事项失败")
        
        # 获取更新后的待办事项
        updated_todo = todo_service.get_todo(todo_id)
        
        # 转换为响应格式
        todo_data = {
            "id": updated_todo.id,
            "user_id": updated_todo.user_id,
            "title": updated_todo.title,
            "description": updated_todo.description,
            "completed": updated_todo.completed,
            "priority": updated_todo.priority,
            "note_id": updated_todo.note_id,
            "due_date": updated_todo.due_date.isoformat() if updated_todo.due_date else None,
            "completed_at": updated_todo.completed_at.isoformat() if updated_todo.completed_at else None,
            "created_at": updated_todo.created_at.isoformat() if updated_todo.created_at else None,
            "updated_at": updated_todo.updated_at.isoformat() if updated_todo.updated_at else None,
            "last_updated": updated_todo.last_updated.isoformat() if updated_todo.last_updated else None,
            "is_overdue": updated_todo.is_overdue(),
            "status_display": updated_todo.get_status_display()
        }
        
        return TodoResponse(
            success=True,
            message="待办事项更新成功",
            data=todo_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新待办事项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新待办事项失败: {str(e)}")


@todo_router.delete("/{user_id}/{todo_id}")
async def delete_todo(
    user_id: int = Path(..., description="用户ID"),
    todo_id: int = Path(..., description="待办事项ID"),
    current_user: Dict[str, Any] = CurrentUser
):
    """
    删除待办事项
    
    Args:
        user_id: 用户ID
        todo_id: 待办事项ID
        current_user: 当前认证用户
        
    Returns:
        删除待办事项响应
    """
    try:
        # 验证用户只能删除自己的待办事项
        if str(user_id) != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="无权删除其他用户的待办事项")
        
        # 使用服务管理器获取待办事项服务
        todo_service = service_manager.get_service(
            'todo_service',
            TodoService
        )
        
        # 先获取待办事项验证存在性和权限
        todo = todo_service.get_todo(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="待办事项不存在")
        
        if todo.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权删除此待办事项")
        
        # 删除待办事项
        success = todo_service.delete_todo(todo_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="删除待办事项失败")
        
        return TodoResponse(
            success=True,
            message="待办事项删除成功",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除待办事项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除待办事项失败: {str(e)}") 