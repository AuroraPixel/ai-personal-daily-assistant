import React, { useState, useEffect } from 'react';
import { useAppSelector } from '../store/hooks';
import { AuthManager } from '../lib/auth';

interface WebSocketTesterProps {
  isOpen: boolean;
  onClose: () => void;
}

export const WebSocketTester: React.FC<WebSocketTesterProps> = ({ isOpen, onClose }) => {
  const { user, token } = useAppSelector((state) => state.auth);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [status, setStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  const [logs, setLogs] = useState<string[]>([]);
  const [testMessage, setTestMessage] = useState('Hello from WebSocket tester');

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const testConnection = () => {
    if (!user || !token) {
      addLog('❌ 错误：缺少用户信息或token');
      return;
    }

    if (ws && ws.readyState === WebSocket.OPEN) {
      addLog('⚠️ 连接已存在，先关闭');
      ws.close();
    }

    setStatus('connecting');
    addLog('🔌 开始测试WebSocket连接...');

    // 构建WebSocket URL
    const wsUrl = new URL('/ws', window.location.origin);
    wsUrl.protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    wsUrl.searchParams.set('user_id', String(user.user_id));
    wsUrl.searchParams.set('username', user.username);
    wsUrl.searchParams.set('token', token);

    if (import.meta.env.DEV) {
      wsUrl.host = 'localhost:8000';
    }

    addLog(`📡 连接URL: ${wsUrl.toString()}`);
    addLog(`👤 用户ID: ${user.user_id} (类型: ${typeof user.user_id})`);
    addLog(`🎫 Token长度: ${token.length}`);

    const websocket = new WebSocket(wsUrl.toString());

    websocket.onopen = () => {
      addLog('✅ WebSocket连接成功');
      setStatus('connected');
    };

    websocket.onmessage = (event) => {
      addLog(`📥 收到消息: ${event.data}`);
      try {
        const data = JSON.parse(event.data);
        addLog(`📄 解析后: ${JSON.stringify(data, null, 2)}`);
      } catch (e) {
        addLog(`❌ JSON解析失败: ${e}`);
      }
    };

    websocket.onclose = (event) => {
      addLog(`🔌 连接关闭: 代码=${event.code}, 原因="${event.reason}", 正常=${event.wasClean}`);
      setStatus('disconnected');
      
      // 分析关闭原因
      switch (event.code) {
        case 4001:
          addLog('❌ 分析：JWT令牌无效或已过期');
          break;
        case 4003:
          addLog('❌ 分析：用户ID与令牌不匹配');
          break;
        case 1000:
          addLog('✅ 分析：正常关闭');
          break;
        default:
          addLog(`⚠️ 分析：异常关闭（代码：${event.code}）`);
      }
    };

    websocket.onerror = (error) => {
      addLog(`❌ WebSocket错误: ${error}`);
      setStatus('error');
    };

    setWs(websocket);
  };

  const sendTestMessage = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      addLog('❌ 连接未建立，无法发送消息');
      return;
    }

    const message = {
      type: 'chat',
      content: testMessage,
      timestamp: new Date().toISOString()
    };

    addLog(`📤 发送测试消息: ${JSON.stringify(message)}`);
    ws.send(JSON.stringify(message));
  };

  const disconnect = () => {
    if (ws) {
      addLog('🔌 手动断开连接');
      ws.close(1000, 'Manual disconnect');
      setWs(null);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const checkTokenInfo = () => {
    if (!token) {
      addLog('❌ 没有token');
      return;
    }

    addLog('🔍 检查token信息...');
    addLog(`🎫 Token: ${token.substring(0, 50)}...`);
    
    // 检查本地存储
    const storedToken = AuthManager.getToken();
    const storedUser = AuthManager.getUser();
    addLog(`💾 本地存储token: ${storedToken?.substring(0, 50)}...`);
    addLog(`👤 本地存储用户: ${JSON.stringify(storedUser)}`);
    
    // 检查token是否过期
    const isExpired = AuthManager.isTokenExpired();
    addLog(`⏰ Token是否过期: ${isExpired}`);
  };

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-11/12 max-w-4xl h-5/6 flex flex-col">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold">WebSocket 连接测试器</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ×
          </button>
        </div>
        
        <div className="flex-1 p-4 flex gap-4">
          {/* 控制面板 */}
          <div className="w-1/3 flex flex-col gap-4">
            <div className="p-3 bg-gray-50 rounded">
              <h3 className="font-medium mb-2">连接状态</h3>
              <div className={`inline-block px-2 py-1 rounded text-sm ${
                status === 'connected' ? 'bg-green-100 text-green-800' :
                status === 'connecting' ? 'bg-yellow-100 text-yellow-800' :
                status === 'error' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {status}
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <button
                onClick={testConnection}
                disabled={status === 'connecting'}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {status === 'connecting' ? '连接中...' : '测试连接'}
              </button>
              
              <button
                onClick={checkTokenInfo}
                className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
              >
                检查Token信息
              </button>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={testMessage}
                  onChange={(e) => setTestMessage(e.target.value)}
                  placeholder="测试消息"
                  className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                />
                <button
                  onClick={sendTestMessage}
                  disabled={status !== 'connected'}
                  className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 text-sm"
                >
                  发送
                </button>
              </div>

              <button
                onClick={disconnect}
                disabled={status === 'disconnected'}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
              >
                断开连接
              </button>

              <button
                onClick={clearLogs}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                清空日志
              </button>
            </div>
          </div>

          {/* 日志面板 */}
          <div className="flex-1">
            <h3 className="font-medium mb-2">连接日志</h3>
            <div className="h-full bg-gray-50 rounded p-3 overflow-y-auto font-mono text-sm">
              {logs.length === 0 ? (
                <div className="text-gray-500">点击"测试连接"开始...</div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="mb-1">
                    {log}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 