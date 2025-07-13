// 开发配置
export const config = {
  // 是否使用WebSocket (true: 使用WebSocket, false: 使用Mock数据)
  USE_WEBSOCKET: true,
  
  // WebSocket配置
  WEBSOCKET_URL: import.meta.env.DEV ? 'ws://localhost:8000' : window.location.origin,
  
  // 默认用户配置
  DEFAULT_USER_ID: '1',
  DEFAULT_USERNAME: '测试用户',
  
  // 调试模式
  DEBUG: import.meta.env.DEV,
};

// 导出配置项
export const { USE_WEBSOCKET, WEBSOCKET_URL, DEFAULT_USER_ID, DEFAULT_USERNAME, DEBUG } = config; 