import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { createWebSocketService } from './lib/websocket.ts'
import { DEFAULT_USER_ID, DEFAULT_USERNAME } from './lib/config.ts'

// =================================================================
// 全局初始化 WebSocket 连接
// 确保在整个应用生命周期中只执行一次
// =================================================================
console.log('🚀 应用启动，初始化全局 WebSocket 服务...');
const wsService = createWebSocketService(DEFAULT_USER_ID, DEFAULT_USERNAME);
wsService.connect().catch(error => {
  console.error('❌ 全局 WebSocket 连接失败:', error);
});
// =================================================================

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
