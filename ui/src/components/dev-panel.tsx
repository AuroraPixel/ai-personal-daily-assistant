import { useState } from "react";

interface DevPanelProps {
  onSendMessage: (message: string) => void;
}

export function DevPanel({ onSendMessage }: DevPanelProps) {
  const [isVisible, setIsVisible] = useState(false);

  const testScenarios = [
    {
      name: "基本查询",
      message: "我想查询我的航班信息",
    },
    {
      name: "座位选择",
      message: "我想选择座位",
    },
    {
      name: "航班变更",
      message: "我需要变更我的航班",
    },
    {
      name: "行李问题",
      message: "我的行李丢失了",
    },
    {
      name: "投诉建议",
      message: "我要投诉服务质量",
    },
  ];

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 bg-purple-600 text-white p-3 rounded-full shadow-lg hover:bg-purple-700 transition-colors z-50"
        title="显示开发测试面板"
      >
        🛠️
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-50 min-w-64">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold text-sm">开发测试面板</h3>
        <button
          onClick={() => setIsVisible(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>
      
      <div className="space-y-2">
        <div className="text-xs text-gray-600 mb-2">
          快速测试场景：
        </div>
        {testScenarios.map((scenario) => (
          <button
            key={scenario.name}
            onClick={() => onSendMessage(scenario.message)}
            className="w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded border transition-colors"
          >
            {scenario.name}
          </button>
        ))}
      </div>
      
      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600 mb-2">
          提示：
        </div>
        <div className="text-xs text-gray-500 space-y-1">
          <div>• 输入包含"座位"的消息会显示座位图</div>
          <div>• 输入包含"航班变更"的消息会切换代理</div>
          <div>• 所有数据都是模拟的，用于开发测试</div>
        </div>
      </div>
    </div>
  );
} 