import React, { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { logout } from "../store/slices/authSlice";
import { AgentPanel } from "../components/agent-panel";
import { Chat } from "../components/Chat";
import { DevPanel } from "../components/dev-panel";
import { WebSocketTester } from "../components/WebSocketTester";
import ErrorBoundary from "../components/ErrorBoundary";
import type { Agent, AgentEvent, GuardrailCheck, Message } from "../lib/types";
import { createWebSocketService, getWebSocketService, type WebSocketConnectionStatus } from "../lib/websocket";
import { Bot, MessageCircle, Wifi, WifiOff, RefreshCw, AlertTriangle, LogOut, User, Settings } from "lucide-react";
import { Button } from "../components/ui/button";

const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user, token } = useAppSelector((state) => state.auth);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>("");
  const [guardrails, setGuardrails] = useState<GuardrailCheck[]>([]);
  const [context, setContext] = useState<Record<string, any>>({});
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationMessages, setConversationMessages] = useState<Record<string, Message[]>>({});
  const [activeTab, setActiveTab] = useState<'agent' | 'customer'>('agent');
  const [wsStatus, setWsStatus] = useState<WebSocketConnectionStatus>('disconnected');
  const [streamingResponse, setStreamingResponse] = useState<string>('');
  const [wsError, setWsError] = useState<string>('');
  const [debugInfo, setDebugInfo] = useState<string[]>([]);
  const [showTester, setShowTester] = useState<boolean>(false);

  // 设置WebSocket事件监听器
  useEffect(() => {
    console.log('🔗 Dashboard useEffect 触发:', { 
      hasUser: !!user, 
      hasToken: !!token, 
      userId: user?.user_id,
      username: user?.username,
      isAuthenticated: !!user && !!token
    });
    
    if (!user || !token) {
      console.warn('❌ 用户信息或token缺失，跳过WebSocket连接');
      setWsStatus('disconnected');
      return;
    }

    console.log('🔗 Dashboard 组件已挂载，开始监听 WebSocket 事件...');
    
    // 确保user_id是字符串格式
    const userId = typeof user.user_id === 'string' ? user.user_id : String(user.user_id);
    
    // 使用认证用户信息创建WebSocket连接
    const wsService = createWebSocketService(userId, user.username, undefined, token);
    
    if (wsService) {
      // 监听连接状态
      const handleStatus = (status: WebSocketConnectionStatus) => {
        console.log('📡 Dashboard 收到状态更新:', status);
        setWsStatus(status);
        setDebugInfo(prev => [...prev, `状态更新: ${status} - ${new Date().toLocaleTimeString()}`]);
        
        if (status === 'connected') {
          setWsError('');
        }
      };
      
      // 监听连接成功事件
      const handleConnected = (content: any) => {
        console.log('🎉 WebSocket连接成功:', content);
        setWsStatus('connected');
        setWsError('');
        setDebugInfo(prev => [...prev, `连接成功 - ${new Date().toLocaleTimeString()}`]);
      };
      
      // 监听连接错误事件
      const handleError = (content: any) => {
        console.error('❌ WebSocket连接错误:', content);
        setWsStatus('error');
        const errorMsg = content?.error || '未知错误';
        setWsError(errorMsg);
        setDebugInfo(prev => [...prev, `连接错误: ${errorMsg} - ${new Date().toLocaleTimeString()}`]);
        
        // 重置loading状态
        setIsLoading(false);
        setStreamingResponse('');
      };
      
      // 监听认证错误事件
      const handleAuthError = (content: any) => {
        console.error('❌ WebSocket认证错误:', content);
        setWsStatus('error');
        const errorMsg = content?.error || '认证失败';
        setWsError(errorMsg);
        setDebugInfo(prev => [...prev, `认证错误: ${errorMsg} - ${new Date().toLocaleTimeString()}`]);
        
        // 重置loading状态
        setIsLoading(false);
        setStreamingResponse('');
      };
      
      // 监听AI错误事件
      const handleAIError = (content: any) => {
        console.error('❌ AI处理错误:', content);
        const errorMsg = content?.error || 'AI处理失败';
        setDebugInfo(prev => [...prev, `AI错误: ${errorMsg} - ${new Date().toLocaleTimeString()}`]);
        
        // 重置loading状态
        setIsLoading(false);
        setStreamingResponse('');
      };
      
      // 监听实时流式响应
      const handleStreamingResponse = (content: any) => {
        console.log('🔄 Dashboard 收到流式响应:', content);
        
        if (typeof content !== 'object' || content === null) {
          console.warn('收到的 content 不是一个有效的对象:', content);
          return;
        }
        
        // 处理流式响应 - 修复：直接使用content作为ChatResponse对象
        if (content.type === 'completion') {
          // 流式响应完成
          console.log('✅ 流式响应完成:', content);
          setStreamingResponse('');
          setIsLoading(false);
          
          // 处理最终响应
          if (content.final_response) {
            handleChatResponse(content.final_response);
          }
        } else {
          // 流式响应更新 - content本身就是ChatResponse对象
          console.log('🔄 流式响应更新:', content);
          
          // 更新流式响应文本
          if (content.raw_response) {
            setStreamingResponse(content.raw_response);
          }
          
          // 实时更新其他状态
          if (content.conversation_id) {
            setConversationId(content.conversation_id);
          }
          
          if (content.current_agent) {
            setCurrentAgent(content.current_agent);
          }
          
          if (content.messages && Array.isArray(content.messages)) {
            const newMessages = content.messages.map((msg: any) => ({
              id: `${Date.now()}-${Math.random()}`,
              content: msg.content,
              type: msg.agent === 'user' ? 'user' : 'ai',
              agent: msg.agent,
              timestamp: new Date(),
            }));
            setMessages(newMessages);
          }
          
          if (content.events && Array.isArray(content.events)) {
            setEvents(content.events);
          }
          
          if (content.agents && Array.isArray(content.agents)) {
            setAgents(content.agents);
          }
          
          if (content.guardrails && Array.isArray(content.guardrails)) {
            setGuardrails(content.guardrails);
          }
          
          if (content.context) {
            setContext(content.context);
          }
        }
      };
      
      // 监听聊天响应
      const handleChatResponse = (response: any) => {
        console.log('💬 Dashboard 收到聊天响应:', response);
        
        try {
          if (response.conversation_id) {
            setConversationId(response.conversation_id);
          }
          
          if (response.current_agent) {
            setCurrentAgent(response.current_agent);
          }
          
          if (response.messages && Array.isArray(response.messages)) {
            const newMessages = response.messages.map((msg: any) => ({
              id: `${Date.now()}-${Math.random()}`,
              content: msg.content,
              type: msg.agent === 'user' ? 'user' : 'ai',
              agent: msg.agent,
              timestamp: new Date(),
            }));
            setMessages(newMessages);
            
            // 更新会话消息记录
            if (response.conversation_id) {
              setConversationMessages(prev => ({
                ...prev,
                [response.conversation_id]: newMessages
              }));
            }
          }
          
          if (response.events && Array.isArray(response.events)) {
            setEvents(response.events);
          }
          
          if (response.agents && Array.isArray(response.agents)) {
            setAgents(response.agents);
          }
          
          if (response.guardrails && Array.isArray(response.guardrails)) {
            setGuardrails(response.guardrails);
          }
          
          if (response.context) {
            setContext(response.context);
          }
          
          // 注意：不再在这里设置isLoading为false，因为已经在流式响应完成时设置了
          
        } catch (error) {
          console.error('处理聊天响应时出错:', error);
          setIsLoading(false);
        }
      };
      
      // 注册事件监听器
      wsService.on('status', handleStatus);
      wsService.on('connected', handleConnected);
      wsService.on('error', handleError);
      wsService.on('auth_error', handleAuthError);
      wsService.on('ai_error', handleAIError);
      wsService.on('ai_response', handleStreamingResponse);
      wsService.on('ai_thinking', handleStreamingResponse);
      wsService.on('ai_finished', handleStreamingResponse);
      wsService.on('chat_response', handleChatResponse);
      
      // 建立连接
      console.log('🔌 开始建立WebSocket连接...');
      setDebugInfo(prev => [...prev, `开始连接WebSocket - ${new Date().toLocaleTimeString()}`]);
      setDebugInfo(prev => [...prev, `用户ID: ${userId}, 用户名: ${user.username}`]);
      
      wsService.connect()
        .then(() => {
          console.log('✅ WebSocket连接建立成功');
          setDebugInfo(prev => [...prev, `连接建立成功 - ${new Date().toLocaleTimeString()}`]);
        })
        .catch((error) => {
          console.error('❌ WebSocket连接失败:', error);
          setWsStatus('error');
          const errorMsg = error?.message || '连接失败';
          setWsError(errorMsg);
          setDebugInfo(prev => [...prev, `连接失败: ${errorMsg} - ${new Date().toLocaleTimeString()}`]);
        });
      
      // 清理函数
      return () => {
        console.log('🧹 清理WebSocket事件监听器');
        wsService.off('status', handleStatus);
        wsService.off('connected', handleConnected);
        wsService.off('error', handleError);
        wsService.off('auth_error', handleAuthError);
        wsService.off('ai_error', handleAIError);
        wsService.off('ai_response', handleStreamingResponse);
        wsService.off('ai_thinking', handleStreamingResponse);
        wsService.off('ai_finished', handleStreamingResponse);
        wsService.off('chat_response', handleChatResponse);
      };
    } else {
      console.error('❌ 无法创建WebSocket服务');
      setWsStatus('error');
    }
  }, [user, token]);

  // 其他业务逻辑方法
  const handleSelectConversation = async (selectedConversationId: string) => {
    console.log('🔄 选择会话:', selectedConversationId);
    setConversationId(selectedConversationId);
    
    // 获取或创建WebSocket服务
    const wsService = getWebSocketService();
    if (wsService) {
      wsService.setConversationId(selectedConversationId);
      
      // 如果有缓存的消息，直接使用
      if (conversationMessages[selectedConversationId]) {
        setMessages(conversationMessages[selectedConversationId]);
        return;
      }
      
      // 否则重新获取消息
      setMessages([]);
      setIsLoading(true);
      
      try {
        // 这里可以添加获取历史消息的逻辑
        console.log('📜 获取会话历史消息:', selectedConversationId);
        setIsLoading(false);
      } catch (error) {
        console.error('获取会话历史消息失败:', error);
        setIsLoading(false);
      }
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;
    
    console.log('📤 发送消息:', content);
    setIsLoading(true);
    setStreamingResponse('');
    
    // 立即添加用户消息到UI
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: content.trim(),
      type: 'user',
      agent: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // 通过WebSocket发送消息
    const wsService = getWebSocketService();
    if (wsService) {
      try {
        wsService.sendChatMessage(content.trim());
      } catch (error) {
        console.error('发送消息失败:', error);
        setIsLoading(false);
        setStreamingResponse('');
      }
    } else {
      console.error('WebSocket 服务未初始化');
      setIsLoading(false);
      setStreamingResponse('');
    }
  };

  const handleLogout = () => {
    dispatch(logout());
  };

  const getStatusIcon = () => {
    switch (wsStatus) {
      case 'connected':
        return <Wifi className="w-5 h-5 text-green-500" />;
      case 'connecting':
        return <RefreshCw className="w-5 h-5 text-yellow-500 animate-spin" />;
      case 'error':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return <WifiOff className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = () => {
    switch (wsStatus) {
      case 'connected':
        return '已连接';
      case 'connecting':
        return '连接中';
      case 'error':
        return '连接错误';
      default:
        return '未连接';
    }
  };

  const getStatusColor = () => {
    switch (wsStatus) {
      case 'connected':
        return 'text-green-600';
      case 'connecting':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <ErrorBoundary>
      <div className="h-screen bg-gray-50 flex flex-col">
        {/* 顶部导航栏 */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">
                AI 个人助手
              </h1>
              <div className="flex items-center space-x-2">
                {getStatusIcon()}
                <span className={`text-sm ${getStatusColor()}`}>
                  {getStatusText()}
                </span>
                {wsError && (
                  <span className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                    {wsError}
                  </span>
                )}
                {/* WebSocket重连按钮 */}
                {wsStatus !== 'connected' && (
                  <button
                    onClick={() => {
                      console.log('🔄 手动重连WebSocket...');
                      setDebugInfo(prev => [...prev, `手动重连WebSocket - ${new Date().toLocaleTimeString()}`]);
                      
                      if (user && token) {
                        const userId = typeof user.user_id === 'string' ? user.user_id : String(user.user_id);
                        const wsService = createWebSocketService(userId, user.username, undefined, token);
                        wsService.connect()
                          .then(() => {
                            console.log('✅ 手动重连成功');
                            setDebugInfo(prev => [...prev, `手动重连成功 - ${new Date().toLocaleTimeString()}`]);
                          })
                          .catch((error) => {
                            console.error('❌ 手动重连失败:', error);
                            setDebugInfo(prev => [...prev, `手动重连失败: ${error.message} - ${new Date().toLocaleTimeString()}`]);
                          });
                      }
                    }}
                    className="text-xs text-blue-600 hover:text-blue-700 px-2 py-1 bg-blue-50 rounded border border-blue-200 hover:bg-blue-100"
                  >
                    重连
                  </button>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="w-5 h-5 text-gray-500" />
                <span className="text-sm text-gray-700">
                  {user?.username || '用户'}
                </span>
              </div>
              {/* 调试信息按钮 */}
              {debugInfo.length > 0 && (
                <div className="relative group">
                  <button className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 bg-gray-100 rounded">
                    调试信息
                  </button>
                  <div className="absolute right-0 top-full mt-1 w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-3 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                    <div className="text-xs text-gray-600 space-y-1 max-h-40 overflow-y-auto">
                      {debugInfo.slice(-10).map((info, index) => (
                        <div key={index} className="font-mono">{info}</div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              {/* WebSocket测试器按钮 */}
              <button
                onClick={() => setShowTester(true)}
                className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 bg-gray-100 rounded border border-gray-200 hover:bg-gray-200 flex items-center gap-1"
                title="WebSocket连接测试器"
              >
                <Settings className="w-3 h-3" />
                测试器
              </button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <LogOut className="w-4 h-4 mr-1" />
                退出
              </Button>
            </div>
          </div>
        </header>

        {/* 主要内容区域 */}
        <div className="flex-1 flex overflow-hidden">
          {/* 桌面端布局 */}
          <div className="hidden md:flex flex-1">
                                      {/* 左侧面板 */}
             <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
               <AgentPanel
                 agents={agents}
                 currentAgent={currentAgent}
                 events={events}
                 guardrails={guardrails}
                 context={context}
               />
             </div>

             {/* 中间聊天区域 */}
             <div className="flex-1 flex flex-col">
               <Chat
                 messages={messages}
                 onSendMessage={handleSendMessage}
                 isLoading={isLoading}
                 streamingResponse={streamingResponse}
                 wsStatus={wsStatus}
                 conversationId={conversationId}
                 onSelectConversation={handleSelectConversation}
               />
             </div>

             {/* 右侧开发面板 */}
             <div className="w-80 bg-white border-l border-gray-200">
               <DevPanel
                 onSendMessage={handleSendMessage}
               />
             </div>
          </div>

          {/* 移动端布局 */}
          <div className="md:hidden flex-1 flex flex-col">
            {/* 移动端标签切换 */}
            <div className="bg-white border-b border-gray-200 px-4 py-2">
              <div className="flex space-x-1">
                <button
                  onClick={() => setActiveTab('agent')}
                  className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'agent'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Bot className="w-4 h-4 mx-auto mb-1" />
                  智能体
                </button>
                <button
                  onClick={() => setActiveTab('customer')}
                  className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'customer'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <MessageCircle className="w-4 h-4 mx-auto mb-1" />
                  聊天
                </button>
              </div>
            </div>

                         {/* 移动端内容 */}
             <div className="flex-1 overflow-hidden">
               {activeTab === 'agent' ? (
                 <AgentPanel
                   agents={agents}
                   currentAgent={currentAgent}
                   events={events}
                   guardrails={guardrails}
                   context={context}
                 />
               ) : (
                 <Chat
                   messages={messages}
                   onSendMessage={handleSendMessage}
                   isLoading={isLoading}
                   streamingResponse={streamingResponse}
                   wsStatus={wsStatus}
                   conversationId={conversationId}
                   onSelectConversation={handleSelectConversation}
                 />
               )}
             </div>
          </div>
        </div>
        
        {/* WebSocket测试器 */}
        {showTester && (
          <WebSocketTester
            isOpen={showTester}
            onClose={() => setShowTester(false)}
          />
        )}
      </div>
    </ErrorBoundary>
  );
};

export default Dashboard; 