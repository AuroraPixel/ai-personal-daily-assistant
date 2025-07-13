import { useEffect, useState } from "react";
import { AgentPanel } from "./components/agent-panel";
import { Chat } from "./components/Chat";
import { DevPanel } from "./components/dev-panel";
import ErrorBoundary from "./components/ErrorBoundary";
import type { Agent, AgentEvent, GuardrailCheck, Message } from "./lib/types";

import { createWebSocketService, getWebSocketService, type WebSocketConnectionStatus } from "./lib/websocket";
import { DEFAULT_USER_ID, DEFAULT_USERNAME } from "./lib/config";
import { Bot, MessageCircle, Wifi, WifiOff, RefreshCw, AlertTriangle } from "lucide-react";

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>("");
  const [guardrails, setGuardrails] = useState<GuardrailCheck[]>([]);
  const [context, setContext] = useState<Record<string, any>>({});
  const [conversationId, setConversationId] = useState<string | null>(null);
  // Loading state while awaiting assistant response
  const [isLoading, setIsLoading] = useState(false);
  // Mobile tab state
  const [activeTab, setActiveTab] = useState<'agent' | 'customer'>('agent');
  // WebSocket connection status
  const [wsStatus, setWsStatus] = useState<WebSocketConnectionStatus>('disconnected');
  // Real-time streaming response
  const [streamingResponse, setStreamingResponse] = useState<string>('');

  // Setup WebSocket event listeners
  useEffect(() => {
    console.log('🔗 App 组件已挂载，开始监听 WebSocket 事件...');
    // 连接已在 main.tsx 中全局创建，这里只需获取实例并监听事件
    const wsService = getWebSocketService();
    
    if (wsService) {
      // 监听连接状态
      const handleStatus = (status: WebSocketConnectionStatus) => {
        console.log('📡 App.tsx 收到状态更新:', status);
        setWsStatus(status);
      };
      
      // 监听实时流式响应
      const handleStreamingResponse = (content: any) => {
        console.log('🔄 App.tsx 收到流式响应:', content);
        
        if (typeof content !== 'object' || content === null) {
          console.warn('收到的 content 不是一个有效的对象:', content);
          return;
        }
        
        if (content.conversation_id && !conversationId) {
          setConversationId(content.conversation_id);
        }
        
        if (content.current_agent) {
          setCurrentAgent(content.current_agent);
        }
        
        if (content.context) {
          setContext(content.context);
        }
        
        if (content.events) {
          const stamped = content.events.map((e: any) => ({
            ...e,
            timestamp: e.timestamp ?? Date.now(),
          }));
          setEvents((prev) => [...prev, ...stamped]);
        }
        
        if (content.agents) {
          setAgents(content.agents);
        }
        
        if (content.guardrails) {
          setGuardrails(content.guardrails);
        }
        
        // 处理流式响应
        if (typeof content.raw_response === 'string' && content.type !== 'completion') {
          setStreamingResponse(content.raw_response);
        }
        
        // 处理完成的消息
        if (Array.isArray(content.messages) && content.type === 'completion') {
          const newMessages: Message[] = content.messages
            .filter((m: any) => m && typeof m.content === 'string' && typeof m.agent === 'string')
            .map((m: any) => ({
              id: Date.now().toString() + Math.random().toString(),
              content: m.content,
              role: "assistant",
              agent: m.agent,
              timestamp: new Date(),
            }));
          
          if (newMessages.length > 0) {
            setMessages((prev) => [...prev, ...newMessages]);
          }
          
          setStreamingResponse('');
          setIsLoading(false);
        }
      };
      
      // 绑定事件
      wsService.on('status', handleStatus);
      wsService.on('ai_response', handleStreamingResponse);
      
      // 立即用当前状态更新一次UI
      handleStatus(wsService.status);
      
      // 清理函数
      return () => {
        console.log('🧹 App 组件卸载，清理 WebSocket 事件监听器');
        wsService.off('status', handleStatus);
        wsService.off('ai_response', handleStreamingResponse);
      };
    } else {
      console.error('❌ WebSocket 服务在 App.tsx 中未找到');
    }
  }, []); // 空依赖数组确保只在挂载和卸载时执行

  // Send a user message
  const handleSendMessage = async (content: string) => {
    console.log('💬 用户发送消息:', content);
    
    const userMsg: Message = {
      id: Date.now().toString(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setStreamingResponse('');

    try {
      const wsService = getWebSocketService();
      if (wsService && wsService.status === 'connected') {
        console.log('📤 通过WebSocket发送消息');
        wsService.sendChatMessage(content);
      } else {
        console.error('❌ WebSocket未连接，无法发送消息');
        setIsLoading(false);
        return;
      }
    } catch (error) {
      console.error('❌ 发送消息失败:', error);
      setIsLoading(false);
    }
  };

  // WebSocket status indicator
  const getStatusIcon = () => {
    switch (wsStatus) {
      case 'connected':
        return <Wifi className="h-4 w-4 text-green-500" />;
      case 'connecting':
        return <RefreshCw className="h-4 w-4 text-yellow-500 animate-spin" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'disconnected':
      default:
        return <WifiOff className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusText = () => {
    switch (wsStatus) {
      case 'connected':
        return '已连接';
      case 'connecting':
        return '连接中...';
      case 'error':
        return '连接错误';
      case 'disconnected':
      default:
        return '连接断开';
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
      case 'disconnected':
      default:
        return 'text-red-600';
    }
  };

  return (
    <div className="h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Bot className="h-6 w-6 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-800">
            AI Personal Assistant
          </h1>
        </div>
        
        {/* WebSocket Status */}
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>
      </div>

      {/* Mobile Tab Bar */}
      <div className="md:hidden bg-white border-b border-gray-200 flex">
        <button
          onClick={() => setActiveTab('agent')}
          className={`flex-1 py-3 px-4 text-sm font-medium flex items-center justify-center gap-2 ${
            activeTab === 'agent' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'
          }`}
        >
          <Bot className="h-4 w-4" />
          Agent Panel
        </button>
        <button
          onClick={() => setActiveTab('customer')}
          className={`flex-1 py-3 px-4 text-sm font-medium flex items-center justify-center gap-2 ${
            activeTab === 'customer' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'
          }`}
        >
          <MessageCircle className="h-4 w-4" />
          Customer View
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex w-full overflow-hidden">
        {/* Agent Panel */}
        <div className={`${activeTab === 'agent' ? 'flex' : 'hidden'} md:flex flex-1 h-full`}>
          <AgentPanel
            agents={agents}
            currentAgent={currentAgent}
            events={events}
            guardrails={guardrails}
            context={context}
          />
        </div>

        {/* Customer Chat */}
        <div className={`${activeTab === 'customer' ? 'flex' : 'hidden'} md:flex flex-1 h-full`}>
          <ErrorBoundary>
            <Chat
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              streamingResponse={streamingResponse}
              wsStatus={wsStatus}
            />
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
}

export default App;
