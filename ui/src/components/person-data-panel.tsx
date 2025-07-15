import React, { useState, useEffect } from 'react';
import { FileText, CheckSquare, User, Database } from 'lucide-react';
import { Button } from './ui/button';
import { NotesPanel } from './notes-panel';
import { TodosPanel } from './todos-panel';
import type { PersonDataTab } from '../lib/types';
import { useAppSelector } from '../store/hooks';

interface PersonDataPanelProps {
  userId?: number;
}

export function PersonDataPanel({ userId }: PersonDataPanelProps) {
  const [activeTab, setActiveTab] = useState<PersonDataTab>('notes');
  const [currentUserId, setCurrentUserId] = useState<number>(userId || 1);
  
  // 从 Redux store 获取用户信息
  const { user } = useAppSelector(state => state.auth);
  
  useEffect(() => {
    if (user?.user_id) {
      setCurrentUserId(parseInt(user.user_id));
    } else if (userId) {
      setCurrentUserId(userId);
    }
  }, [user, userId]);

  return (
    <div className="w-full h-full flex flex-col bg-transparent">
      {/* 头部 */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-600 text-white h-12 px-4 flex items-center gap-3 shadow-sm md:rounded-t-xl flex-shrink-0">
        <Database className="h-5 w-5" />
        <h1 className="font-semibold text-sm sm:text-base lg:text-lg">Person Data</h1>
        <span className="ml-auto text-xs font-light tracking-wide opacity-80">
          个人数据管理
        </span>
      </div>

      {/* 标签切换 */}
      <div className="border-b bg-gray-50">
        <div className="flex">
          <button
            onClick={() => setActiveTab('notes')}
            className={`flex-1 py-3 px-4 text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
              activeTab === 'notes'
                ? 'bg-white text-purple-600 border-b-2 border-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>笔记</span>
          </button>
          <button
            onClick={() => setActiveTab('todos')}
            className={`flex-1 py-3 px-4 text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
              activeTab === 'todos'
                ? 'bg-white text-purple-600 border-b-2 border-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
            }`}
          >
            <CheckSquare className="w-4 h-4" />
            <span>待办事项</span>
          </button>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-hidden bg-white">
        {activeTab === 'notes' && <NotesPanel userId={currentUserId} />}
        {activeTab === 'todos' && <TodosPanel userId={currentUserId} />}
      </div>
    </div>
  );
} 