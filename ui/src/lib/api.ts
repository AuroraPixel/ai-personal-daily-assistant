import { mockChatResponse, mockEvents } from './mockData';
import { createWebSocketService, getWebSocketService, type ChatResponse } from './websocket';
import type { Message, AgentEvent, GuardrailCheck, Agent } from './types';
import { USE_WEBSOCKET, DEFAULT_USER_ID, DEFAULT_USERNAME, DEBUG } from './config';
import { chatAPI } from '../services/apiService';

// 开发模式使用 mock 数据
const USE_MOCK_DATA = !USE_WEBSOCKET;

// 数据格式转换函数
function convertChatResponseToFrontend(chatResponse: ChatResponse): {
  conversation_id: string;
  current_agent: string;
  messages: Array<{content: string; agent: string}>;
  events: AgentEvent[];
  context: Record<string, any>;
  agents: Agent[];
  guardrails: GuardrailCheck[];
} {
  return {
    conversation_id: chatResponse.conversation_id,
    current_agent: chatResponse.current_agent,
    messages: chatResponse.messages || [],
    events: (chatResponse.events || []).map(event => ({
      id: event.id,
      type: event.type as any,
      agent: event.agent,
      content: event.content,
      timestamp: event.timestamp ? new Date(event.timestamp) : new Date(),
      metadata: event.metadata
    })),
    context: chatResponse.context || {},
    agents: (chatResponse.agents || []).map(agent => ({
      name: agent.name || '',
      description: agent.description || '',
      handoffs: agent.handoffs || [],
      tools: agent.tools || [],
      input_guardrails: agent.input_guardrails || []
    })),
    guardrails: (chatResponse.guardrails || []).map(guard => ({
      id: guard.id,
      name: guard.name,
      input: guard.input,
      reasoning: guard.reasoning,
      passed: guard.passed,
      timestamp: new Date(guard.timestamp)
    }))
  };
}

// WebSocket API 实现
class WebSocketAPI {
  private currentChatResponse: ChatResponse | null = null;
  private responsePromise: Promise<any> | null = null;
  private resolveResponse: ((value: any) => void) | null = null;
  private rejectResponse: ((reason?: any) => void) | null = null;

  async initializeWebSocket(userId: string, username?: string): Promise<void> {
    const wsService = createWebSocketService(userId, username);
    
    // 监听AI响应事件
    wsService.on('ai_response', (content) => {
      this.handleAIResponse(content);
    });
    
    // 监听连接事件
    wsService.on('connected', (content) => {
      console.log('WebSocket连接成功:', content);
    });
    
    // 监听错误事件
    wsService.on('ai_error', (content) => {
      console.error('AI错误:', content);
      if (this.rejectResponse) {
        this.rejectResponse(new Error(content.error || 'AI处理失败'));
      }
    });
    
    // 监听连接状态
    wsService.on('status', (status) => {
      console.log('WebSocket状态:', status);
    });
    
    // 建立连接
    await wsService.connect();
    
    // 等待初始连接确认
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  private handleAIResponse(content: any) {
    if (typeof content === 'object') {
      if (content.type === 'completion') {
        // 对话完成
        this.currentChatResponse = content.final_response;
        console.log('对话完成, 最终响应:', this.currentChatResponse);
        
        if (this.resolveResponse && this.currentChatResponse) {
          const convertedResponse = convertChatResponseToFrontend(this.currentChatResponse);
          this.resolveResponse(convertedResponse);
          this.resolveResponse = null;
          this.rejectResponse = null;
        }
      } else {
        // 流式响应更新
        this.currentChatResponse = content;
        console.log('流式响应更新:', this.currentChatResponse);
        
        // 可以在这里实现实时UI更新
        // 暂时不处理，等待最终响应
      }
    }
  }

  async sendMessage(message: string, conversationId: string): Promise<any> {
    const wsService = getWebSocketService();
    if (!wsService) {
      throw new Error('WebSocket服务未初始化');
    }

    // 创建新的Promise来等待响应
    this.responsePromise = new Promise((resolve, reject) => {
      this.resolveResponse = resolve;
      this.rejectResponse = reject;
      
      // 设置超时
      setTimeout(() => {
        if (this.rejectResponse) {
          this.rejectResponse(new Error('响应超时'));
        }
      }, 30000); // 30秒超时
    });

    // 发送消息
    wsService.sendChatMessage(message);
    
    // 等待响应
    return this.responsePromise;
  }

  async getInitialResponse(): Promise<any> {
    // 发送空消息获取初始响应
    return this.sendMessage('', '');
  }
}

// 创建WebSocket API实例
const wsAPI = new WebSocketAPI();

// Helper to call the server
export async function callChatAPI(message: string, conversationId: string) {
  if (USE_MOCK_DATA) {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 根据消息内容返回不同的响应
    if (message.includes("座位") || message.includes("seat")) {
      return {
        ...mockChatResponse,
        messages: [
          {
            content: "DISPLAY_SEAT_MAP",
            agent: "Customer Service Agent"
          }
        ]
      };
    }
    
    if (message.includes("航班变更") || message.includes("change")) {
      return {
        ...mockChatResponse,
        current_agent: "Flight Change Agent",
        messages: [
          {
            content: "我来帮您处理航班变更。请提供您希望更改到的新航班信息。",
            agent: "Flight Change Agent"
          }
        ],
        events: [
          ...mockEvents,
          {
            id: "event_handoff",
            type: "handoff",
            agent: "Flight Change Agent",
            content: "从客户服务代理转移到航班变更代理",
            timestamp: new Date(),
            metadata: {
              source_agent: "Customer Service Agent",
              target_agent: "Flight Change Agent"
            }
          }
        ]
      };
    }
    
    return {
      ...mockChatResponse,
      messages: [
        {
          content: message ? 
            `我理解您的问题："${message}"。让我为您查找相关信息。` : 
            "您好！我是航空公司的客户服务代理。今天我可以为您提供什么帮助吗？",
          agent: "Customer Service Agent"
        }
      ]
    };
  }

  if (USE_WEBSOCKET) {
    try {
      // 如果是首次调用（空消息），初始化WebSocket
      // 注意：这个函数现在已废弃，因为WebSocket在Dashboard中直接管理
      if (!message && !conversationId) {
        console.warn('callChatAPI: 此函数已废弃，请在Dashboard中直接使用WebSocket服务');
        return null;
      }
      
      // 发送消息
      return await wsAPI.sendMessage(message, conversationId);
    } catch (error) {
      console.error('WebSocket API错误:', error);
      return null;
    }
  }

  // 原有的HTTP API调用（保留作为备用）
  try {
    const response = await chatAPI.sendChatMessage({
      conversation_id: conversationId,
      message: message
    });
    return response.data;
  } catch (err) {
    console.error("Error sending message:", err);
    return null;
  }
} 