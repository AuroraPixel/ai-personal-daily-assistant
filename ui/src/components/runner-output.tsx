import { Terminal, ArrowRight, Wrench, FileText } from "lucide-react";
import type { AgentEvent } from "../lib/types";

interface RunnerOutputProps {
  runnerEvents: AgentEvent[];
}

export function RunnerOutput({ runnerEvents }: RunnerOutputProps) {
  const getEventIcon = (type: string) => {
    switch (type) {
      case "handoff":
        return <ArrowRight className="h-4 w-4 text-blue-600" />;
      case "tool_call":
        return <Wrench className="h-4 w-4 text-green-600" />;
      case "tool_output":
        return <FileText className="h-4 w-4 text-purple-600" />;
      case "context_update":
        return <Database className="h-4 w-4 text-orange-600" />;
      default:
        return <Terminal className="h-4 w-4 text-gray-600" />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case "handoff":
        return "border-blue-200 bg-blue-50";
      case "tool_call":
        return "border-green-200 bg-green-50";
      case "tool_output":
        return "border-purple-200 bg-purple-50";
      case "context_update":
        return "border-orange-200 bg-orange-50";
      default:
        return "border-gray-200 bg-gray-50";
    }
  };

  const formatTimestamp = (timestamp: number | string | Date): string => {
    try {
      if (!timestamp) return '';
      // 确保 timestamp 是一个 Date 对象
      const date = new Date(timestamp);
      // 检查转换后的日期是否有效
      if (isNaN(date.getTime())) {
        return 'Invalid Date';
      }
      return date.toLocaleTimeString();
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return 'Time Error';
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Terminal className="h-4 w-4 text-gray-600" />
        <h3 className="font-semibold text-sm text-gray-900">
          运行输出
        </h3>
      </div>
      
      {runnerEvents.length === 0 && (
        <div className="text-xs text-gray-500 italic">
          暂无运行事件
        </div>
      )}
      
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {runnerEvents.map((event) => (
          <div
            key={event.id}
            className={`p-3 rounded-lg border ${getEventColor(event.type)}`}
          >
            <div className="flex items-start gap-2">
              {getEventIcon(event.type)}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-gray-900 uppercase">
                    {event.type}
                  </span>
                  <span className="text-xs text-gray-600">
                    by {event.agent}
                  </span>
                </div>
                <p className="text-xs text-gray-700">
                  {event.content}
                </p>
                
                {event.metadata && (
                  <div className="mt-2 p-2 bg-white bg-opacity-50 rounded text-xs">
                    <div className="font-medium text-gray-700 mb-1">元数据:</div>
                    {Object.entries(event.metadata).map(([key, value], index) => (
                      <div key={`metadata-${event.id}-${index}-${key}`} className="flex justify-between">
                        <span className="text-gray-600">{key}:</span>
                        <span className="text-gray-900 font-mono">
                          {typeof value === 'string' ? value : JSON.stringify(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="text-xs text-gray-400 mt-2">
              {formatTimestamp(event.timestamp)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Database({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <ellipse cx="12" cy="5" rx="9" ry="3"/>
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
    </svg>
  );
} 