import React, { useState, useRef, useEffect, useCallback } from "react";
import type { Message } from "../lib/types";
import ReactMarkdown from "react-markdown";
import { SeatMap } from "./seat-map";
import type { WebSocketConnectionStatus } from "../lib/websocket";
import { Wifi, WifiOff, RefreshCw, Send, AlertCircle, Menu } from "lucide-react";
import { ConversationList } from "./ConversationList";
import { useAppSelector } from "../store/hooks";

// 打字机效果的样式
const typewriterStyles = `
  .typewriter-content {
    overflow: hidden;
    border-right: 2px solid transparent;
    white-space: normal;
    word-wrap: break-word;
  }
  
  .typewriter-cursor {
    animation: blink 1s infinite;
  }
  
  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }
`;

interface ChatProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  /** Whether waiting for assistant response */
  isLoading?: boolean;
  /** Real-time streaming response */
  streamingResponse?: string;
  /** WebSocket connection status */
  wsStatus?: WebSocketConnectionStatus;
  /** Current conversation ID */
  conversationId?: string | null;
  /** Callback when conversation is selected */
  onSelectConversation?: (conversationId: string) => void;
}

export function Chat({ 
  messages, 
  onSendMessage, 
  isLoading, 
  streamingResponse, 
  wsStatus = 'disconnected',
  conversationId,
  onSelectConversation
}: ChatProps) {
  const { user } = useAppSelector((state) => state.auth);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputText, setInputText] = useState("");
  const [isComposing, setIsComposing] = useState(false);
  const [showSeatMap, setShowSeatMap] = useState(false);
  const [selectedSeat, setSelectedSeat] = useState<string | undefined>(undefined);
  const [isSending, setIsSending] = useState(false);
  const [lastError, setLastError] = useState<string>("");
  const [showConversationList, setShowConversationList] = useState(false);

  // Auto-scroll to bottom when messages or loading indicator change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "instant" });
  }, [messages, isLoading]);

  // Watch for special seat map trigger message (anywhere in list) and only if a seat has not been picked yet
  useEffect(() => {
    const hasTrigger = messages.some(
      (m) => m.type === "ai" && m.content === "DISPLAY_SEAT_MAP"
    );
    // Show map if trigger exists and seat not chosen yet
    if (hasTrigger && !selectedSeat) {
      setShowSeatMap(true);
    }
  }, [messages, selectedSeat]);

  const handleSend = useCallback(async () => {
    if (!inputText.trim()) return;
    
    if (wsStatus !== 'connected') {
      setLastError("连接已断开，请等待自动重连...");
      return;
    }

    setIsSending(true);
    setLastError("");
    
    try {
      await onSendMessage(inputText);
      setInputText("");
    } catch (error) {
      setLastError("发送失败，请重试");
      console.error('发送消息失败:', error);
    } finally {
      setIsSending(false);
    }
  }, [inputText, onSendMessage, wsStatus]);

  const handleSeatSelect = useCallback(
    (seat: string) => {
      setSelectedSeat(seat);
      setShowSeatMap(false);
      onSendMessage(`I would like seat ${seat}`);
    },
    [onSendMessage]
  );

  const handleConversationSelect = useCallback(
    (selectedConversationId: string) => {
      if (onSelectConversation) {
        onSelectConversation(selectedConversationId);
      }
      setShowConversationList(false);
    },
    [onSelectConversation]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey && !isComposing) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend, isComposing]
  );

  const getConnectionStatusInfo = () => {
    switch (wsStatus) {
      case 'connected':
        return {
          icon: <Wifi className="h-4 w-4 text-green-500" />,
          text: "已连接",
          color: "text-green-600"
        };
      case 'connecting':
        return {
          icon: <RefreshCw className="h-4 w-4 text-yellow-500 animate-spin" />,
          text: "连接中...",
          color: "text-yellow-600"
        };
      case 'error':
        return {
          icon: <WifiOff className="h-4 w-4 text-red-500" />,
          text: "连接错误",
          color: "text-red-600"
        };
      case 'disconnected':
      default:
        return {
          icon: <WifiOff className="h-4 w-4 text-red-500" />,
          text: "连接断开",
          color: "text-red-600"
        };
    }
  };

  const statusInfo = getConnectionStatusInfo();

  return (
    <div className="flex flex-col h-full flex-1 bg-white shadow-md border border-gray-300 border-t-0 rounded-xl relative">
      <style>{typewriterStyles}</style>
      <div className="bg-blue-600 text-white h-12 px-4 flex items-center justify-between rounded-t-xl border-b border-blue-500">
        <h2 className="font-semibold text-sm sm:text-base lg:text-lg">
          Customer View
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowConversationList(true)}
            className="p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-md transition-all duration-200 text-blue-100 hover:text-white"
            title="会话列表"
          >
            <Menu className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Connection warning */}
      {wsStatus !== 'connected' && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mx-4 mt-2 rounded-r border border-yellow-200">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-yellow-600 mr-2" />
            <div className="text-sm text-yellow-800">
              {wsStatus === 'connecting' && (
                <span>正在尝试连接到服务器...</span>
              )}
              {wsStatus === 'error' && (
                <div>
                  <div>WebSocket连接失败，聊天功能不可用</div>
                  <div className="text-xs mt-1">
                    可能原因：1) 后端服务未启动 2) 认证失败 3) 网络问题
                  </div>
                </div>
              )}
              {wsStatus === 'disconnected' && (
                <span>连接已断开，部分功能可能无法使用</span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto min-h-0 md:px-4 pt-4 pb-20">
        {messages.map((msg, idx) => {
          if (msg.content === "DISPLAY_SEAT_MAP") return null; // Skip rendering marker message
          return (
            <div
              key={idx}
              className={`flex mb-6 text-sm ${msg.type === "user" ? "justify-end" : "justify-start"
                }`}
            >
              {msg.type === "user" ? (
                <div className="ml-4 rounded-2xl rounded-br-md px-5 py-3 md:ml-24 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-medium max-w-[80%] shadow-lg border border-blue-600 transform hover:scale-[1.02] transition-all duration-200">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                <div className="mr-4 rounded-2xl rounded-bl-md px-5 py-3 md:mr-24 text-gray-800 bg-gradient-to-r from-gray-50 to-gray-100 font-medium max-w-[80%] shadow-md border border-gray-300 transform hover:scale-[1.02] transition-all duration-200">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              )}
            </div>
          );
        })}
        {showSeatMap && (
          <div className="flex justify-start mb-5">
            <div className="mr-4 rounded-[16px] rounded-bl-[4px] md:mr-24">
              <SeatMap
                onSeatSelect={handleSeatSelect}
                selectedSeat={selectedSeat}
              />
            </div>
          </div>
        )}
        {streamingResponse && (
          <div className="flex mb-6 text-sm justify-start">
            <div className="mr-4 rounded-2xl rounded-bl-md px-5 py-3 md:mr-24 text-gray-800 bg-gradient-to-r from-blue-50 to-blue-100 font-medium max-w-[80%] shadow-md border border-blue-200 transform hover:scale-[1.02] transition-all duration-200">
              <div className="text-xs text-blue-600 font-semibold mb-2 flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                AI 正在回复...
              </div>
              <div className="typewriter-content">
                <ReactMarkdown>{streamingResponse}</ReactMarkdown>
                <span className="typewriter-cursor inline-block w-0.5 h-4 bg-blue-500 ml-1"></span>
              </div>
            </div>
          </div>
        )}
        {isLoading && !streamingResponse && (
          <div className="flex mb-6 text-sm justify-start">
            <div className="mr-4 rounded-2xl rounded-bl-md px-5 py-3 md:mr-24 bg-gradient-to-r from-gray-50 to-gray-100 font-medium max-w-[80%] shadow-md border border-gray-200">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <span className="text-sm text-gray-700 font-medium">正在处理...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-2 md:px-4">
        {/* Error message */}
        {lastError && (
          <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-red-500" />
            {lastError}
          </div>
        )}

        {/* Status indicator */}
        {isSending && (
          <div className="mb-2 p-2 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700 flex items-center gap-2">
            <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
            正在发送消息...
          </div>
        )}

        <div className="flex items-center">
          <div className="flex w-full items-center pb-4 md:pb-1">
            <div className={`flex w-full flex-col rounded-2xl p-3 bg-white border-2 transition-all duration-200 ${
              wsStatus !== 'connected' 
                ? 'border-gray-200 bg-gray-50' 
                : 'border-blue-200 shadow-lg hover:shadow-xl focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100'
            }`}>
              <div className="flex items-end gap-3">
                <div className="flex min-w-0 flex-1 flex-col">
                  <textarea
                    id="prompt-textarea"
                    tabIndex={0}
                    dir="auto"
                    rows={1}
                    placeholder={
                      wsStatus !== 'connected' 
                        ? "连接断开，无法发送消息"
                        : "在这里输入您的消息..."
                    }
                    className={`resize-none border focus:outline-none text-sm px-2 py-3 rounded-lg transition-all duration-200 ${
                      wsStatus !== 'connected' 
                        ? 'bg-gray-50 text-gray-400 border-gray-200' 
                        : 'bg-gray-50 hover:bg-gray-100 focus:bg-white text-gray-900 placeholder-gray-500 border-gray-300 focus:border-blue-500'
                    }`}
                    style={{ minHeight: '44px', maxHeight: '120px' }}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onCompositionStart={() => setIsComposing(true)}
                    onCompositionEnd={() => setIsComposing(false)}
                    disabled={wsStatus !== 'connected'}
                  />
                </div>
                <button
                  disabled={wsStatus !== 'connected' || !inputText.trim() || isSending}
                  className={`flex h-11 w-11 items-center justify-center rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 border ${
                    wsStatus !== 'connected' || !inputText.trim() || isSending
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed border-gray-300'
                      : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 hover:shadow-lg transform hover:scale-105 focus:ring-blue-300 border-blue-600'
                  }`}
                  onClick={handleSend}
                >
                  {isSending ? (
                    <RefreshCw className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Conversation List */}
      <ConversationList
        isOpen={showConversationList}
        onClose={() => setShowConversationList(false)}
        onSelectConversation={handleConversationSelect}
        currentConversationId={conversationId || null}
        userId={user?.user_id ? parseInt(String(user.user_id)) : 1}
      />
    </div>
  );
} 