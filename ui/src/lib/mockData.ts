// Mock数据定义
export const mockChatResponse = {
  conversation_id: 'mock-conversation-1',
  current_agent: 'Customer Service Agent',
  messages: [],
  events: [],
  context: {},
  agents: [],
  guardrails: [],
  raw_response: '',
  is_finished: false
};

export const mockEvents = [
  {
    id: 'mock-event-1',
    type: 'message',
    agent: 'Customer Service Agent',
    content: 'Mock event content',
    timestamp: new Date(),
    metadata: {}
  }
]; 