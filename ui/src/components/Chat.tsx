import React, { useState, useRef, useEffect, useCallback } from "react";
import type { Message } from "../lib/types";
import ReactMarkdown from "react-markdown";
import { SeatMap } from "./seat-map";
import type { WebSocketConnectionStatus } from "../lib/websocket";
import { Wifi, WifiOff, RefreshCw, Send, AlertCircle } from "lucide-react";

interface ChatProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  /** Whether waiting for assistant response */
  isLoading?: boolean;
  /** Real-time streaming response */
  streamingResponse?: string;
  /** WebSocket connection status */
  wsStatus?: WebSocketConnectionStatus;
}

export function Chat({ 
  messages, 
  onSendMessage, 
  isLoading, 
  streamingResponse, 
  wsStatus = 'disconnected'
}: ChatProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputText, setInputText] = useState("");
  const [isComposing, setIsComposing] = useState(false);
  const [showSeatMap, setShowSeatMap] = useState(false);
  const [selectedSeat, setSelectedSeat] = useState<string | undefined>(undefined);
  const [isSending, setIsSending] = useState(false);
  const [lastError, setLastError] = useState<string>("");

  // Auto-scroll to bottom when messages or loading indicator change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "instant" });
  }, [messages, isLoading]);

  // Watch for special seat map trigger message (anywhere in list) and only if a seat has not been picked yet
  useEffect(() => {
    const hasTrigger = messages.some(
      (m) => m.role === "assistant" && m.content === "DISPLAY_SEAT_MAP"
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
    <div className="flex flex-col h-full flex-1 bg-white shadow-sm border border-gray-200 border-t-0 rounded-xl">
      <div className="bg-blue-600 text-white h-12 px-4 flex items-center justify-between rounded-t-xl">
        <h2 className="font-semibold text-sm sm:text-base lg:text-lg">
          Customer View
        </h2>
        <div className="flex items-center gap-2">
          {statusInfo.icon}
          <span className="text-xs font-medium text-blue-100">
            {statusInfo.text}
          </span>
        </div>
      </div>

      {/* Connection warning */}
      {wsStatus !== 'connected' && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mx-4 mt-2 rounded-r">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-yellow-600 mr-2" />
            <span className="text-sm text-yellow-800">
              {wsStatus === 'connecting'
                ? "正在尝试连接到服务器..." 
                : "连接已断开，部分功能可能无法使用"}
            </span>
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
              className={`flex mb-5 text-sm ${msg.role === "user" ? "justify-end" : "justify-start"
                }`}
            >
              {msg.role === "user" ? (
                <div className="ml-4 rounded-[16px] rounded-br-[4px] px-4 py-2 md:ml-24 bg-black text-white font-light max-w-[80%]">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                <div className="mr-4 rounded-[16px] rounded-bl-[4px] px-4 py-2 md:mr-24 text-zinc-900 bg-[#ECECF1] font-light max-w-[80%]">
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
          <div className="flex mb-5 text-sm justify-start">
            <div className="mr-4 rounded-[16px] rounded-bl-[4px] px-4 py-2 md:mr-24 text-zinc-900 bg-blue-100/50 font-light max-w-[80%] border border-blue-200/50">
              <div className="text-xs text-blue-600 font-medium mb-1 flex items-center gap-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                AI 正在回复...
              </div>
              <ReactMarkdown>{streamingResponse}</ReactMarkdown>
            </div>
          </div>
        )}
        {isLoading && !streamingResponse && (
          <div className="flex mb-5 text-sm justify-start">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 bg-gray-400 rounded-full animate-pulse"></div>
              <div className="h-2 w-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="h-2 w-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              <span className="text-xs text-gray-500 ml-2">正在处理...</span>
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
            <div className={`flex w-full flex-col gap-1.5 rounded-2xl p-2.5 pl-1.5 bg-white border transition-colors ${
              wsStatus !== 'connected' 
                ? 'border-gray-300 bg-gray-50' 
                : 'border-green-200 shadow-sm'
            }`}>
              <div className="flex items-end gap-1.5 md:gap-2 pl-4">
                <div className="flex min-w-0 flex-1 flex-col">
                  <textarea
                    id="prompt-textarea"
                    tabIndex={0}
                    dir="auto"
                    rows={2}
                    placeholder={
                      wsStatus !== 'connected' 
                        ? "连接断开，无法发送消息"
                        : "输入消息..."
                    }
                    className={`mb-2 resize-none border-0 focus:outline-none text-sm px-0 pb-6 pt-2 ${
                      wsStatus !== 'connected' ? 'bg-gray-50 text-gray-400' : 'bg-transparent'
                    }`}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onCompositionStart={() => setIsComposing(true)}
                    onCompositionEnd={() => setIsComposing(false)}
                    disabled={wsStatus !== 'connected'}
                  />
                </div>
                <button
                  disabled={wsStatus !== 'connected' || !inputText.trim()}
                  className={`flex h-8 w-8 items-center justify-center rounded-full transition-colors focus:outline-none ${
                    wsStatus !== 'connected' || !inputText.trim()
                      ? 'bg-gray-300 text-gray-400 cursor-not-allowed'
                      : 'bg-black text-white hover:opacity-70'
                  }`}
                  onClick={handleSend}
                >
                  {isSending ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 