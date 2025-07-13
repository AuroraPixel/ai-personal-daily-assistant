import { Database } from "lucide-react";

interface ConversationContextProps {
  context: Record<string, any>;
}

export function ConversationContext({ context }: ConversationContextProps) {
  const contextEntries = Object.entries(context).filter(([_, value]) => value);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Database className="h-4 w-4 text-gray-600" />
        <h3 className="font-semibold text-sm text-gray-900">
          对话上下文
        </h3>
      </div>
      
      {contextEntries.length === 0 && (
        <div className="text-xs text-gray-500 italic">
          暂无上下文信息
        </div>
      )}
      
      <div className="bg-white border border-gray-200 rounded-lg p-3">
        <div className="grid grid-cols-1 gap-2">
          {contextEntries.map(([key, value]) => (
            <div key={key} className="flex justify-between items-center">
              <span className="text-xs font-medium text-gray-600 capitalize">
                {key.replace(/_/g, ' ')}:
              </span>
              <span className="text-xs text-gray-900 font-mono">
                {typeof value === 'string' ? value : JSON.stringify(value)}
              </span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="text-xs text-gray-400">
        上下文信息会在对话过程中动态更新
      </div>
    </div>
  );
} 