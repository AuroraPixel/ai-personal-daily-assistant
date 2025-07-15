import React, { useState, useEffect } from 'react';
import { 
  CheckSquare, 
  Plus, 
  Calendar, 
  AlertCircle, 
  Edit3, 
  Trash2,
  X,
  Save,
  Clock,
  Flag,
  CheckCircle,
  Circle,
  BarChart3
} from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import type { Todo, TodoCreateRequest, TodoUpdateRequest, PersonDataFilter } from '../lib/types';
import { TodoService } from '../services/personDataService';

interface TodosPanelProps {
  userId: number;
}

export function TodosPanel({ userId }: TodosPanelProps) {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [filter, setFilter] = useState<PersonDataFilter>({});
  const [showStats, setShowStats] = useState(false);
  
  // 表单状态
  const [formData, setFormData] = useState<TodoCreateRequest>({
    title: '',
    description: '',
    priority: 'medium',
    due_date: undefined,
    note_id: undefined
  });

  // 加载待办事项列表
  const loadTodos = async () => {
    try {
      setLoading(true);
      const response = await TodoService.getUserTodos(userId, {
        completed: filter.completed,
        priority: filter.priority,
        overdue: filter.overdue,
        limit: 50
      });
      setTodos(response.data);
    } catch (error) {
      console.error('加载待办事项失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载统计信息
  const loadStats = async () => {
    try {
      const response = await TodoService.getTodoStats(userId);
      setStats(response.data);
    } catch (error) {
      console.error('加载统计信息失败:', error);
    }
  };

  // 创建待办事项
  const createTodo = async () => {
    try {
      const createData = {
        ...formData,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : undefined
      };
      
      const response = await TodoService.createTodo(userId, createData);
      if (response.success) {
        setShowCreateForm(false);
        setFormData({ title: '', description: '', priority: 'medium', due_date: undefined, note_id: undefined });
        loadTodos();
        loadStats();
      }
    } catch (error) {
      console.error('创建待办事项失败:', error);
    }
  };

  // 更新待办事项
  const updateTodo = async () => {
    if (!editingTodo) return;

    try {
      const updateData: TodoUpdateRequest = {
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : undefined,
        note_id: formData.note_id
      };
      
      const response = await TodoService.updateTodo(userId, editingTodo.id, updateData);
      if (response.success) {
        setEditingTodo(null);
        setFormData({ title: '', description: '', priority: 'medium', due_date: undefined, note_id: undefined });
        loadTodos();
        loadStats();
      }
    } catch (error) {
      console.error('更新待办事项失败:', error);
    }
  };

  // 删除待办事项
  const deleteTodo = async (todoId: number) => {
    if (!confirm('确定要删除这个待办事项吗？')) return;

    try {
      const response = await TodoService.deleteTodo(userId, todoId);
      if (response.success) {
        loadTodos();
        loadStats();
      }
    } catch (error) {
      console.error('删除待办事项失败:', error);
    }
  };

  // 切换完成状态
  const toggleComplete = async (todo: Todo) => {
    try {
      if (todo.completed) {
        await TodoService.uncompleteTodo(userId, todo.id);
      } else {
        await TodoService.completeTodo(userId, todo.id);
      }
      loadTodos();
      loadStats();
    } catch (error) {
      console.error('切换完成状态失败:', error);
    }
  };

  // 开始编辑
  const startEdit = (todo: Todo) => {
    setEditingTodo(todo);
    setFormData({
      title: todo.title,
      description: todo.description,
      priority: todo.priority,
      due_date: todo.due_date ? new Date(todo.due_date).toISOString().split('T')[0] : undefined,
      note_id: todo.note_id || undefined
    });
    setShowCreateForm(true);
  };

  // 取消编辑
  const cancelEdit = () => {
    setEditingTodo(null);
    setShowCreateForm(false);
    setFormData({ title: '', description: '', priority: 'medium', due_date: undefined, note_id: undefined });
  };

  // 格式化日期
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // 获取优先级颜色
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-green-500';
      default: return 'text-gray-500';
    }
  };

  // 获取优先级背景色
  const getPriorityBgColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // 获取优先级文本
  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'high': return '高';
      case 'medium': return '中';
      case 'low': return '低';
      default: return '中';
    }
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadTodos();
    loadStats();
  }, [userId, filter]);

  return (
    <div className="h-full flex flex-col">
      {/* 头部 */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <CheckSquare className="w-5 h-5" />
          待办事项
        </h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowStats(!showStats)}
            className="flex items-center gap-1"
          >
            <BarChart3 className="w-4 h-4" />
            统计
          </Button>
          <Button 
            onClick={() => setShowCreateForm(true)}
            className="bg-green-500 hover:bg-green-600"
            size="sm"
          >
            <Plus className="w-4 h-4 mr-1" />
            新建任务
          </Button>
        </div>
      </div>

      {/* 统计信息 */}
      {showStats && stats && (
        <div className="p-4 border-b bg-gray-50">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
              <div className="text-sm text-gray-600">总计</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
              <div className="text-sm text-gray-600">已完成</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{stats.pending}</div>
              <div className="text-sm text-gray-600">进行中</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
              <div className="text-sm text-gray-600">已过期</div>
            </div>
          </div>
        </div>
      )}

      {/* 过滤器 */}
      <div className="p-4 border-b space-y-3">
        <div className="flex gap-2">
          <select
            value={filter.completed !== undefined ? filter.completed.toString() : ''}
            onChange={(e) => setFilter({ 
              ...filter, 
              completed: e.target.value === '' ? undefined : e.target.value === 'true'
            })}
            className="px-3 py-1 border rounded text-sm"
          >
            <option value="">全部状态</option>
            <option value="false">未完成</option>
            <option value="true">已完成</option>
          </select>
          
          <select
            value={filter.priority || ''}
            onChange={(e) => setFilter({ ...filter, priority: (e.target.value || undefined) as 'high' | 'medium' | 'low' | undefined })}
            className="px-3 py-1 border rounded text-sm"
          >
            <option value="">全部优先级</option>
            <option value="high">高优先级</option>
            <option value="medium">中优先级</option>
            <option value="low">低优先级</option>
          </select>
          
          <select
            value={filter.overdue !== undefined ? filter.overdue.toString() : ''}
            onChange={(e) => setFilter({ 
              ...filter, 
              overdue: e.target.value === '' ? undefined : e.target.value === 'true'
            })}
            className="px-3 py-1 border rounded text-sm"
          >
            <option value="">全部任务</option>
            <option value="true">已过期</option>
            <option value="false">未过期</option>
          </select>
        </div>
      </div>

      {/* 待办事项列表 */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
          </div>
        ) : todos.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            暂无待办事项
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {todos.map((todo) => (
              <Card key={todo.id} className={`p-4 hover:shadow-md transition-shadow ${
                todo.completed ? 'opacity-75' : ''
              }`}>
                <div className="flex items-start gap-3">
                  <button
                    onClick={() => toggleComplete(todo)}
                    className="mt-1 flex-shrink-0"
                  >
                    {todo.completed ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <Circle className="w-5 h-5 text-gray-400 hover:text-green-500" />
                    )}
                  </button>
                  
                  <div className="flex-1">
                    <h3 className={`font-medium mb-1 ${
                      todo.completed ? 'line-through text-gray-500' : 'text-gray-900'
                    }`}>
                      {todo.title}
                    </h3>
                    
                    {todo.description && (
                      <p className="text-sm text-gray-600 mb-2">{todo.description}</p>
                    )}
                    
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full ${getPriorityBgColor(todo.priority)}`}>
                        <Flag className="w-3 h-3" />
                        {getPriorityText(todo.priority)}
                      </span>
                      
                      {todo.due_date && (
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full ${
                          todo.is_overdue ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                        }`}>
                          <Calendar className="w-3 h-3" />
                          {formatDate(todo.due_date)}
                        </span>
                      )}
                      
                      {todo.is_overdue && !todo.completed && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-800 rounded-full">
                          <AlertCircle className="w-3 h-3" />
                          已过期
                        </span>
                      )}
                      
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                        <Clock className="w-3 h-3" />
                        {todo.status_display}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex gap-1">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => startEdit(todo)}
                      className="p-1 h-8 w-8"
                    >
                      <Edit3 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteTodo(todo.id)}
                      className="p-1 h-8 w-8 text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* 创建/编辑表单 */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md m-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                {editingTodo ? '编辑待办事项' : '创建待办事项'}
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={cancelEdit}
                className="p-1 h-8 w-8"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  标题
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="请输入待办事项标题"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  描述
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  rows={3}
                  placeholder="请输入待办事项描述"
                />
              </div>
              
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    优先级
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value as 'high' | 'medium' | 'low' })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="low">低优先级</option>
                    <option value="medium">中优先级</option>
                    <option value="high">高优先级</option>
                  </select>
                </div>
                
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    截止日期
                  </label>
                  <input
                    type="date"
                    value={formData.due_date || ''}
                    onChange={(e) => setFormData({ ...formData, due_date: e.target.value || undefined })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex justify-end gap-2 mt-6">
              <Button
                variant="outline"
                onClick={cancelEdit}
              >
                取消
              </Button>
              <Button
                onClick={editingTodo ? updateTodo : createTodo}
                className="bg-green-500 hover:bg-green-600"
                disabled={!formData.title.trim()}
              >
                <Save className="w-4 h-4 mr-1" />
                {editingTodo ? '更新' : '创建'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 