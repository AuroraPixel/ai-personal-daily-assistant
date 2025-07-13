import type { Agent, AgentEvent, GuardrailCheck, Message } from './types';

export const mockAgents: Agent[] = [
  {
    name: "Customer Service Agent",
    description: "主要客户服务代理，处理一般查询和预订",
    handoffs: ["Flight Change Agent", "Baggage Agent"],
    tools: ["get_booking_info", "check_flight_status"],
    input_guardrails: ["politeness_check", "data_privacy_check"]
  },
  {
    name: "Flight Change Agent", 
    description: "专门处理航班变更和重新预订",
    handoffs: ["Customer Service Agent"],
    tools: ["change_flight", "check_availability", "calculate_fees"],
    input_guardrails: ["policy_compliance_check"]
  },
  {
    name: "Baggage Agent",
    description: "处理行李相关问题和申请",
    handoffs: ["Customer Service Agent"],
    tools: ["track_baggage", "file_claim", "update_baggage_status"],
    input_guardrails: ["claim_validation_check"]
  }
];

export const mockMessages: Message[] = [
  {
    id: "1",
    content: "您好！我是航空公司的客户服务代理。今天我可以为您提供什么帮助吗？",
    role: "assistant",
    agent: "Customer Service Agent",
    timestamp: new Date(Date.now() - 60000)
  }
];

export const mockEvents: AgentEvent[] = [
  {
    id: "event_1",
    type: "message",
    agent: "Customer Service Agent",
    content: "初始化客户服务会话",
    timestamp: new Date(Date.now() - 60000)
  },
  {
    id: "event_2", 
    type: "context_update",
    agent: "Customer Service Agent",
    content: "会话上下文已初始化",
    timestamp: new Date(Date.now() - 50000),
    metadata: {
      context_key: "session_id",
      context_value: "sess_123456"
    }
  },
  {
    id: "event_3",
    type: "tool_call",
    agent: "Customer Service Agent", 
    content: "调用工具：get_booking_info",
    timestamp: new Date(Date.now() - 40000),
    metadata: {
      tool_name: "get_booking_info",
      tool_args: { booking_id: "ABC123" }
    }
  }
];

export const mockGuardrails: GuardrailCheck[] = [
  {
    id: "guard_1",
    name: "礼貌检查",
    input: "用户输入内容检查",
    reasoning: "检查用户输入是否包含不当语言或不礼貌表达",
    passed: true,
    timestamp: new Date(Date.now() - 30000)
  },
  {
    id: "guard_2", 
    name: "数据隐私检查",
    input: "敏感信息检查",
    reasoning: "确保不会泄露其他乘客的个人信息",
    passed: true,
    timestamp: new Date(Date.now() - 20000)
  },
  {
    id: "guard_3",
    name: "政策合规检查", 
    input: "航班变更请求",
    reasoning: "检查请求是否符合航空公司政策",
    passed: false,
    timestamp: new Date(Date.now() - 10000)
  }
];

export const mockContext = {
  passenger_name: "张三",
  confirmation_number: "ABC123",
  seat_number: "12A", 
  flight_number: "CA1234",
  account_number: "FF123456789",
  departure_city: "北京",
  arrival_city: "上海",
  departure_time: "2024-01-15 14:30",
  booking_status: "confirmed"
};

export const mockChatResponse = {
  conversation_id: "conv_123456",
  current_agent: "Customer Service Agent",
  context: mockContext,
  events: mockEvents,
  agents: mockAgents,
  guardrails: mockGuardrails,
  messages: [
    {
      content: "我已经找到了您的预订信息。您的航班 CA1234 从北京到上海，座位是 12A。还有什么我可以帮助您的吗？",
      agent: "Customer Service Agent"
    }
  ]
}; 