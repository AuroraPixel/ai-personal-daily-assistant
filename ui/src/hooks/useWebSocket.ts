import { useState, useEffect, useCallback } from 'react';
import { getWebSocketService, type WebSocketConnectionStatus } from '../lib/websocket';

interface UseWebSocketReturn {
  status: WebSocketConnectionStatus;
  isConnected: boolean;
  connect: () => Promise<void>;
  disconnect: () => void;
  sendMessage: (content: string) => void;
  connectionId: string | null;
  error: Error | null;
}

export function useWebSocket(): UseWebSocketReturn {
  const [status, setStatus] = useState<WebSocketConnectionStatus>('disconnected');
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const isConnected = status === 'connected';

  // 连接WebSocket
  const connect = useCallback(async () => {
    try {
      const wsService = getWebSocketService();
      if (wsService) {
        await wsService.connect();
        setError(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('连接失败'));
    }
  }, []);

  // 断开连接
  const disconnect = useCallback(() => {
    const wsService = getWebSocketService();
    if (wsService) {
      wsService.disconnect();
    }
    setConnectionId(null);
    setError(null);
  }, []);

  // 发送消息
  const sendMessage = useCallback((content: string) => {
    const wsService = getWebSocketService();
    if (wsService && isConnected) {
      wsService.sendChatMessage(content);
    } else {
      setError(new Error('未连接到WebSocket服务'));
    }
  }, [isConnected]);

  // 设置事件监听器
  useEffect(() => {
    const wsService = getWebSocketService();
    if (!wsService) return;

    const handleStatus = (newStatus: WebSocketConnectionStatus) => {
      setStatus(newStatus);
      if (newStatus === 'connected') {
        setError(null);
      }
    };

    const handleConnected = (content: any) => {
      setConnectionId(content.connection_id || null);
      console.log('WebSocket连接成功:', content);
    };

    const handleError = (content: any) => {
      setError(new Error(content.error || 'WebSocket错误'));
    };

    wsService.on('status', handleStatus);
    wsService.on('connected', handleConnected);
    wsService.on('error', handleError);
    wsService.on('ai_error', handleError);

    return () => {
      wsService.off('status', handleStatus);
      wsService.off('connected', handleConnected);
      wsService.off('error', handleError);
      wsService.off('ai_error', handleError);
    };
  }, []);

  return {
    status,
    isConnected,
    connect,
    disconnect,
    sendMessage,
    connectionId,
    error,
  };
} 