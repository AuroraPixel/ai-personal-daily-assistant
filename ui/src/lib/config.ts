// 开发配置
export const config = {
  // 是否使用WebSocket (true: 使用WebSocket, false: 使用Mock数据)
  USE_WEBSOCKET: true,
  
  // API基础配置
  API_BASE_URL: import.meta.env.DEV ? 'http://localhost:8000' : window.location.origin,
  
  // WebSocket配置
  WEBSOCKET_URL: import.meta.env.DEV ? 'ws://localhost:8000' : window.location.origin,
  
  // 默认用户配置
  DEFAULT_USER_ID: '1',
  DEFAULT_USERNAME: '测试用户',
  
  // 调试模式
  DEBUG: import.meta.env.DEV,
  
  // API请求超时配置
  REQUEST_TIMEOUT: 10000,
  
  // 分页配置
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 10,
    MAX_PAGE_SIZE: 50,
  },
};

// API端点配置
export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/api/auth/login',
    REFRESH: '/api/auth/refresh',
    LOGOUT: '/api/auth/logout',
  },
  
  // 用户相关
  USER: {
    PROFILE: '/api/auth/me',
    PREFERENCES: '/api/user/preferences',
  },
  
  // 会话相关
  CONVERSATION: {
    LIST: (userId: string) => `/api/conversations/${userId}`,
    DETAIL: (conversationId: string) => `/api/conversations/${conversationId}`,
    CREATE: '/api/conversations',
    UPDATE: (conversationId: string) => `/api/conversations/${conversationId}`,
    DELETE: (conversationId: string) => `/api/conversations/${conversationId}`,
  },
  
  // 消息相关 - 修复端点配置
  MESSAGE: {
    LIST: (conversationId: string) => `/api/conversations/${conversationId}/messages`,
    CREATE: '/api/messages',
  },
  
  // 聊天相关
  CHAT: {
    SEND: '/chat',
  },
  
  // 笔记相关
  NOTE: {
    LIST: (userId: string) => `/api/notes/${userId}`,
    CREATE: (userId: string) => `/api/notes/${userId}`,
    UPDATE: (userId: string, noteId: string) => `/api/notes/${userId}/${noteId}`,
    DELETE: (userId: string, noteId: string) => `/api/notes/${userId}/${noteId}`,
    SEARCH: (userId: string) => `/api/notes/${userId}/search`,
    TAGS: (userId: string) => `/api/notes/${userId}/tags`,
  },
  
  // 待办事项相关
  TODO: {
    LIST: (userId: string) => `/api/todos/${userId}`,
    CREATE: (userId: string) => `/api/todos/${userId}`,
    UPDATE: (userId: string, todoId: string) => `/api/todos/${userId}/${todoId}`,
    DELETE: (userId: string, todoId: string) => `/api/todos/${userId}/${todoId}`,
    COMPLETE: (userId: string, todoId: string) => `/api/todos/${userId}/${todoId}/complete`,
    UNCOMPLETE: (userId: string, todoId: string) => `/api/todos/${userId}/${todoId}/uncomplete`,
    STATS: (userId: string) => `/api/todos/${userId}/stats`,
    BY_NOTE: (userId: string, noteId: string) => `/api/todos/${userId}/by-note/${noteId}`,
  },
};

// 导出配置项
export const { USE_WEBSOCKET, API_BASE_URL, WEBSOCKET_URL, DEFAULT_USER_ID, DEFAULT_USERNAME, DEBUG, REQUEST_TIMEOUT, PAGINATION } = config; 