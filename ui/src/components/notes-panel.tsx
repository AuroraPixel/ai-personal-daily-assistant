import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Plus, 
  Search, 
  Tag, 
  Edit3, 
  Trash2, 
  Filter,
  X,
  Save,
  Search as SearchIcon
} from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import type { Note, NoteCreateRequest, NoteUpdateRequest, PersonDataFilter } from '../lib/types';
import { noteAPI } from '../services/apiService';
import { useAppSelector } from '../store/hooks';

interface NotesPanelProps {
  userId: number;
}

// 预定义的标签选项
const PREDEFINED_TAGS = [
  { value: 'lifestyle tips', label: '生活小贴士' },
  { value: 'cooking advice', label: '烹饪建议' },
  { value: 'weather interpretation', label: '天气解读' },
  { value: 'news context', label: '新闻背景' }
];

export function NotesPanel({ userId }: NotesPanelProps) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(false);
  const [operationLoading, setOperationLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<PersonDataFilter>({});
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  
  // 表单状态
  const [formData, setFormData] = useState<NoteCreateRequest>({
    title: '',
    content: '',
    tag: '',
    status: 'draft'
  });

  // 加载笔记列表
  const loadNotes = async () => {
    try {
      setLoading(true);
      const response = await noteAPI.getNotes(userId.toString(), {
        tag: filter.tag,
        status: filter.status,
        search: filter.search,
        limit: 50
      });
      // 适配后端新数据结构：response.data.data
      setNotes(response.data?.data || []);
    } catch (error) {
      console.error('加载笔记失败:', error);
      setNotes([]); // 出错时设置为空数组
    } finally {
      setLoading(false);
    }
  };

  // 加载可用标签
  const loadTags = async () => {
    try {
      const response = await noteAPI.getTags(userId.toString());
      // 适配后端新数据结构：response.data.data
      setAvailableTags(response.data?.data || []);
    } catch (error) {
      console.error('加载标签失败:', error);
      setAvailableTags([]); // 出错时设置为空数组
    }
  };

  // 搜索笔记
  const searchNotes = async () => {
    if (!searchQuery.trim()) {
      setShowSearchResults(false);
      loadNotes();
      return;
    }

    try {
      setLoading(true);
      const response = await noteAPI.searchNotes(userId.toString(), {
        query: searchQuery,
        tag: filter.tag,
        status: filter.status,
        limit: 20,
        use_vector_search: true
      });
      // 适配后端新数据结构：response.data.data
      setNotes(response.data?.data || []);
      setShowSearchResults(true);
    } catch (error) {
      console.error('搜索笔记失败:', error);
      setNotes([]); // 出错时设置为空数组
    } finally {
      setLoading(false);
    }
  };

  // 创建笔记
  const createNote = async () => {
    try {
      setOperationLoading(true);
      const response = await noteAPI.createNote(userId.toString(), formData);
      if (response.success) {
        // 关闭创建窗口
        setShowCreateForm(false);
        // 重置表单
        setFormData({ title: '', content: '', tag: '', status: 'draft' });
        // 刷新数据
        await Promise.all([loadNotes(), loadTags()]);
        // 成功提示
        console.log('笔记创建成功');
      } else {
        console.error('创建笔记失败:', response.message || '未知错误');
      }
    } catch (error) {
      console.error('创建笔记失败:', error);
    } finally {
      setOperationLoading(false);
    }
  };

  // 更新笔记
  const updateNote = async () => {
    if (!editingNote) return;

    try {
      setOperationLoading(true);
      const updateData: NoteUpdateRequest = {
        title: formData.title,
        content: formData.content,
        tag: formData.tag,
        status: formData.status
      };
      
      const response = await noteAPI.updateNote(userId.toString(), editingNote.id.toString(), updateData);
      if (response.success) {
        // 关闭编辑窗口
        setEditingNote(null);
        setShowCreateForm(false);
        // 重置表单
        setFormData({ title: '', content: '', tag: '', status: 'draft' });
        // 刷新数据
        await Promise.all([loadNotes(), loadTags()]);
        // 成功提示
        console.log('笔记更新成功');
      } else {
        console.error('更新笔记失败:', response.message || '未知错误');
      }
    } catch (error) {
      console.error('更新笔记失败:', error);
    } finally {
      setOperationLoading(false);
    }
  };

  // 删除笔记
  const deleteNote = async (noteId: number) => {
    if (!confirm('确定要删除这个笔记吗？')) return;

    try {
      setOperationLoading(true);
      const response = await noteAPI.deleteNote(userId.toString(), noteId.toString());
      if (response.success) {
        // 刷新数据
        await Promise.all([loadNotes(), loadTags()]);
        // 成功提示
        console.log('笔记删除成功');
      } else {
        console.error('删除笔记失败:', response.message || '未知错误');
      }
    } catch (error) {
      console.error('删除笔记失败:', error);
    } finally {
      setOperationLoading(false);
    }
  };

  // 开始编辑
  const startEdit = (note: Note) => {
    setEditingNote(note);
    setFormData({
      title: note.title,
      content: note.content,
      tag: note.tag || '',
      status: note.status
    });
    setShowCreateForm(true);
  };

  // 取消编辑
  const cancelEdit = () => {
    setEditingNote(null);
    setShowCreateForm(false);
    setFormData({ title: '', content: '', tag: '', status: 'draft' });
  };

  // 获取标签显示名称
  const getTagLabel = (tagValue: string) => {
    const tag = PREDEFINED_TAGS.find(t => t.value === tagValue);
    return tag ? tag.label : tagValue;
  };

  // 格式化日期
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'published': return 'bg-green-100 text-green-800';
      case 'archived': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // 组件挂载时加载数据
  useEffect(() => {
    Promise.all([loadNotes(), loadTags()]).catch(error => {
      console.error('初始化数据加载失败:', error);
    });
  }, [userId, filter]);

  return (
    <div className="h-full flex flex-col">
      {/* 头部 */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <FileText className="w-5 h-5" />
          笔记管理
        </h2>
        <Button 
          onClick={() => setShowCreateForm(true)}
          disabled={operationLoading}
          className="bg-blue-500 hover:bg-blue-600 disabled:opacity-50"
          size="sm"
        >
          <Plus className="w-4 h-4 mr-1" />
          新建笔记
        </Button>
      </div>

      {/* 搜索和过滤 */}
      <div className="p-4 border-b space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="搜索笔记..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && searchNotes()}
            className="w-full pl-10 pr-10 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {searchQuery && (
            <button
              onClick={searchNotes}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-blue-500 hover:text-blue-700"
            >
              <SearchIcon className="w-4 h-4" />
            </button>
          )}
        </div>
        
        <div className="flex gap-2">
          <select
            value={filter.tag || ''}
            onChange={(e) => setFilter({ ...filter, tag: e.target.value || undefined })}
            className="px-3 py-1 border rounded text-sm"
          >
            <option value="">所有标签</option>
            {PREDEFINED_TAGS.map(tag => (
              <option key={tag.value} value={tag.value}>{tag.label}</option>
            ))}
            {(availableTags || []).filter(tag => !PREDEFINED_TAGS.some(pt => pt.value === tag)).map(tag => (
              <option key={tag} value={tag}>{tag}</option>
            ))}
          </select>
          
          <select
            value={filter.status || ''}
            onChange={(e) => setFilter({ ...filter, status: e.target.value || undefined })}
            className="px-3 py-1 border rounded text-sm"
          >
            <option value="">所有状态</option>
            <option value="draft">草稿</option>
            <option value="published">已发布</option>
            <option value="archived">已归档</option>
          </select>
        </div>
      </div>

      {/* 笔记列表 */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : notes.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {showSearchResults ? '没有找到匹配的笔记' : '暂无笔记'}
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {(notes || []).map((note) => (
              <Card key={note.id} className="p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 mb-2">{note.title}</h3>
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2">{note.content}</p>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      {note.tag && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                          <Tag className="w-3 h-3" />
                          {getTagLabel(note.tag)}
                        </span>
                      )}
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(note.status)}`}>
                        {note.status === 'draft' ? '草稿' : note.status === 'published' ? '已发布' : '已归档'}
                      </span>
                      <span>{formatDate(note.last_updated)}</span>
                    </div>
                  </div>
                  <div className="flex gap-1 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => startEdit(note)}
                      disabled={operationLoading}
                      className="p-1 h-8 w-8 disabled:opacity-50"
                    >
                      <Edit3 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteNote(note.id)}
                      disabled={operationLoading}
                      className="p-1 h-8 w-8 text-red-500 hover:text-red-700 disabled:opacity-50"
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
                {editingNote ? '编辑笔记' : '创建笔记'}
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
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="请输入笔记标题"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  内容
                </label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  placeholder="请输入笔记内容"
                />
              </div>
              
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    标签
                  </label>
                  <select
                    value={formData.tag}
                    onChange={(e) => setFormData({ ...formData, tag: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">请选择标签</option>
                    {PREDEFINED_TAGS.map(tag => (
                      <option key={tag.value} value={tag.value}>{tag.label}</option>
                    ))}
                  </select>
                </div>
                
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    状态
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="draft">草稿</option>
                    <option value="published">已发布</option>
                    <option value="archived">已归档</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end gap-2 mt-6">
              <Button
                variant="outline"
                onClick={cancelEdit}
                disabled={operationLoading}
              >
                取消
              </Button>
              <Button
                onClick={editingNote ? updateNote : createNote}
                className="bg-blue-500 hover:bg-blue-600"
                disabled={!formData.title.trim() || operationLoading}
              >
                {operationLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1"></div>
                ) : (
                  <Save className="w-4 h-4 mr-1" />
                )}
                {operationLoading 
                  ? (editingNote ? '更新中...' : '创建中...') 
                  : (editingNote ? '更新' : '创建')
                }
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 