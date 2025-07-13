export interface WebSocketMessage {
  type: string;
  content: any;
  sender_id?: string;
  receiver_id?: string;
  room_id?: string;
  timestamp?: string;
}

export interface ChatResponse {
  conversation_id: string;
  current_agent: string;
  messages: Array<{
    content: string;
    agent: string;
  }>;
  events: Array<{
    id: string;
    type: string;
    agent: string;
    content: string;
    metadata?: any;
    timestamp?: number;
  }>;
  context: Record<string, any>;
  agents: Array<Record<string, any>>;
  raw_response: string;
  guardrails: Array<{
    id: string;
    name: string;
    input: string;
    reasoning: string;
    passed: boolean;
    timestamp: number;
  }>;
}

export type WebSocketConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

export type WebSocketEventHandler = (data: any) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private _userId: string;
  private username?: string;
  
  // 事件处理器
  private handlers: Record<string, WebSocketEventHandler[]> = {};
  
  // 连接状态
  private _status: WebSocketConnectionStatus = 'disconnected';
  
  constructor(userId: string, username?: string) {
    this._userId = userId;
    this.username = username;
  }
  
  get status(): WebSocketConnectionStatus {
    return this._status;
  }
  
  get userId(): string {
    return this._userId;
  }
  
  private setStatus(status: WebSocketConnectionStatus) {
    console.log('📊 WebSocket状态变更:', this._status, '->', status);
    this._status = status;
    this.emit('status', status);
  }
  
  // 连接WebSocket
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        console.log('🔗 WebSocket已经连接，直接返回');
        resolve();
        return;
      }
      
      console.log('🔌 开始建立WebSocket连接...');
      this.setStatus('connecting');
      
      // 构建WebSocket URL
      const wsUrl = new URL('/ws', window.location.origin);
      wsUrl.protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      wsUrl.searchParams.set('user_id', this._userId);
      if (this.username) {
        wsUrl.searchParams.set('username', this.username);
      }
      
      // 如果是开发环境，使用固定端口
      if (import.meta.env.DEV) {
        wsUrl.host = 'localhost:8000';
      }
      
      console.log('🌐 WebSocket URL:', wsUrl.toString());
      
      this.ws = new WebSocket(wsUrl.toString());
      
      this.ws.onopen = () => {
        console.log('✅ WebSocket连接已建立');
        this.setStatus('connected');
        this.reconnectAttempts = 0;
        resolve();
      };
      
      this.ws.onmessage = (event) => {
        console.log('📥 收到WebSocket消息:', event.data);
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('❌ 解析WebSocket消息失败:', error);
        }
      };
      
      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket连接已关闭:', { code: event.code, reason: event.reason });
        this.setStatus('disconnected');
        
        // 非正常关闭时尝试重连
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          console.log('🔄 准备重连...');
          this.scheduleReconnect();
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('❌ WebSocket错误:', error);
        this.setStatus('error');
        reject(error);
      };
    });
  }
  
  // 断开连接
  disconnect() {
    console.log('🔌 手动断开WebSocket连接');
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.setStatus('disconnected');
  }
  
  // 发送消息
  send(message: WebSocketMessage) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket未连接，无法发送消息:', message);
      return;
    }
    
    console.log('📤 发送WebSocket消息:', message);
    this.ws.send(JSON.stringify(message));
  }
  
  // 发送聊天消息
  sendChatMessage(content: string) {
    console.log('💬 发送聊天消息:', content);
    this.send({
      type: 'chat',
      content: content,
      timestamp: new Date().toISOString()
    });
  }
  
  // 处理接收到的消息
  private handleMessage(message: WebSocketMessage) {
    console.log('🔍 处理WebSocket消息:', message);
    const { type, content } = message;
    
    switch (type) {
      case 'ai_response':
        this.emit('ai_response', content);
        break;
      case 'connect':
        console.log('🎉 连接成功消息:', content);
        this.emit('connect', content);
        break;
      case 'error':
        console.error('❌ 服务器错误:', content);
        this.emit('error', content);
        break;
      default:
        console.log('📨 其他消息类型:', type, content);
        this.emit('message', message);
    }
  }
  
  // 安排重连
  private scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    
    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    
    console.log(`🔄 安排重连 (第${this.reconnectAttempts}次)，${delay}ms后重试`);
    
    this.reconnectTimer = setTimeout(async () => {
      try {
        await this.connect();
      } catch (error) {
        console.error('❌ 重连失败:', error);
      }
    }, delay);
  }
  
  // 事件监听器
  on(event: string, handler: WebSocketEventHandler) {
    if (!this.handlers[event]) {
      this.handlers[event] = [];
    }
    this.handlers[event].push(handler);
  }
  
  // 移除事件监听器
  off(event: string, handler: WebSocketEventHandler) {
    if (this.handlers[event]) {
      this.handlers[event] = this.handlers[event].filter(h => h !== handler);
    }
  }
  
  // 触发事件
  private emit(event: string, data: any) {
    if (this.handlers[event]) {
      this.handlers[event].forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`事件处理器执行失败 (${event}):`, error);
        }
      });
    }
  }
}

// 创建全局WebSocket实例
let wsService: WebSocketService | null = null;

export function createWebSocketService(userId: string, username?: string): WebSocketService {
  // 如果已存在服务且用户ID相同，返回现有服务
  if (wsService && wsService.userId === userId) {
    console.log('♻️ 复用现有WebSocket服务');
    return wsService;
  }
  
  // 如果存在不同用户的服务，先断开
  if (wsService) {
    console.log('🔄 断开现有WebSocket服务（用户切换）');
    wsService.disconnect();
  }
  
  console.log('🆕 创建新的WebSocket服务:', { userId, username });
  wsService = new WebSocketService(userId, username);
  return wsService;
}

export function getWebSocketService(): WebSocketService | null {
  return wsService;
} 