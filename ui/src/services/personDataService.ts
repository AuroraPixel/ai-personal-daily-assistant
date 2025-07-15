import type { 
  Note, 
  NoteCreateRequest, 
  NoteUpdateRequest, 
  NoteListResponse, 
  NoteResponse,
  NoteSearchResponse,
  Todo,
  TodoCreateRequest,
  TodoUpdateRequest,
  TodoListResponse,
  TodoResponse,
  TodoStatsResponse
} from '../lib/types';
import { getToken } from '../lib/auth';

const API_BASE_URL = 'http://localhost:8000/api';

// 获取认证头
const getAuthHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${getToken()}`
});

// =========================
// 笔记相关API服务
// =========================

export class NoteService {
  // 创建笔记
  static async createNote(userId: number, request: NoteCreateRequest): Promise<NoteResponse> {
    const response = await fetch(`${API_BASE_URL}/notes/${userId}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`创建笔记失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 获取用户笔记列表
  static async getUserNotes(
    userId: number,
    options: {
      tag?: string;
      status?: string;
      search?: string;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<NoteListResponse> {
    const params = new URLSearchParams();
    
    if (options.tag) params.append('tag', options.tag);
    if (options.status) params.append('status', options.status);
    if (options.search) params.append('search', options.search);
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.offset) params.append('offset', options.offset.toString());
    
    const response = await fetch(`${API_BASE_URL}/notes/${userId}?${params}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`获取笔记列表失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 获取单个笔记
  static async getNote(userId: number, noteId: number): Promise<NoteResponse> {
    const response = await fetch(`${API_BASE_URL}/notes/${userId}/${noteId}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`获取笔记失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 更新笔记
  static async updateNote(userId: number, noteId: number, request: NoteUpdateRequest): Promise<NoteResponse> {
    const response = await fetch(`${API_BASE_URL}/notes/${userId}/${noteId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`更新笔记失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 删除笔记
  static async deleteNote(userId: number, noteId: number): Promise<NoteResponse> {
    const response = await fetch(`${API_BASE_URL}/notes/${userId}/${noteId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`删除笔记失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 搜索笔记
  static async searchNotes(
    userId: number,
    query: string,
    options: {
      tag?: string;
      status?: string;
      limit?: number;
    } = {}
  ): Promise<NoteSearchResponse> {
    const params = new URLSearchParams();
    
    if (options.tag) params.append('tag', options.tag);
    if (options.status) params.append('status', options.status);
    if (options.limit) params.append('limit', options.limit.toString());
    
    const response = await fetch(`${API_BASE_URL}/notes/${userId}/search?${params}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ search_query: query })
    });
    
    if (!response.ok) {
      throw new Error(`搜索笔记失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 获取笔记标签
  static async getNoteTags(userId: number): Promise<{ success: boolean; data: { tags: string[] } }> {
    const response = await fetch(`${API_BASE_URL}/notes/${userId}/tags`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`获取笔记标签失败: ${response.statusText}`);
    }
    
    return await response.json();
  }
}

// =========================
// 待办事项相关API服务
// =========================

export class TodoService {
  // 创建待办事项
  static async createTodo(userId: number, request: TodoCreateRequest): Promise<TodoResponse> {
    const response = await fetch(`${API_BASE_URL}/todos/${userId}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`创建待办事项失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 获取用户待办事项列表
  static async getUserTodos(
    userId: number,
    options: {
      completed?: boolean;
      priority?: string;
      overdue?: boolean;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<TodoListResponse> {
    const params = new URLSearchParams();
    
    if (options.completed !== undefined) params.append('completed', options.completed.toString());
    if (options.priority) params.append('priority', options.priority);
    if (options.overdue !== undefined) params.append('overdue', options.overdue.toString());
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.offset) params.append('offset', options.offset.toString());
    
    const response = await fetch(`${API_BASE_URL}/todos/${userId}?${params}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`获取待办事项列表失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 获取单个待办事项
  static async getTodo(userId: number, todoId: number): Promise<TodoResponse> {
    const response = await fetch(`${API_BASE_URL}/todos/${userId}/${todoId}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`获取待办事项失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 更新待办事项
  static async updateTodo(userId: number, todoId: number, request: TodoUpdateRequest): Promise<TodoResponse> {
    const response = await fetch(`${API_BASE_URL}/todos/${userId}/${todoId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`更新待办事项失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 删除待办事项
  static async deleteTodo(userId: number, todoId: number): Promise<TodoResponse> {
    const response = await fetch(`${API_BASE_URL}/todos/${userId}/${todoId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`删除待办事项失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 标记完成
  static async completeTodo(userId: number, todoId: number): Promise<TodoResponse> {
    const response = await fetch(`${API_BASE_URL}/todos/${userId}/${todoId}/complete`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`标记完成失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 取消完成
  static async uncompleteTodo(userId: number, todoId: number): Promise<TodoResponse> {
    const response = await fetch(`${API_BASE_URL}/todos/${userId}/${todoId}/uncomplete`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`取消完成失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 获取统计信息
  static async getTodoStats(userId: number): Promise<TodoStatsResponse> {
    const response = await fetch(`${API_BASE_URL}/todos/${userId}/stats`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`获取统计信息失败: ${response.statusText}`);
    }
    
    return await response.json();
  }

  // 获取关联笔记的待办事项
  static async getTodosByNote(userId: number, noteId: number): Promise<TodoListResponse> {
    const response = await fetch(`${API_BASE_URL}/todos/${userId}/by-note/${noteId}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`获取关联笔记的待办事项失败: ${response.statusText}`);
    }
    
    return await response.json();
  }
} 