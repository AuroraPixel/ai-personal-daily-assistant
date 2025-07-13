# AI 个人日常助手 WebSocket 流式服务

## 功能概述

这个 WebSocket 服务整合了 AI 个人助手的流式输出功能，为每个用户创建独立的房间，支持实时的流式聊天交互。

## 主要特性

- ✅ **用户身份验证**: 要求用户提供用户ID
- ✅ **独立房间**: 每个用户有自己的私人聊天房间
- ✅ **流式输出**: 实时流式返回 AI 响应
- ✅ **ChatResponse 格式**: 标准化的响应格式
- ✅ **多代理支持**: 支持天气、新闻、菜谱等多种代理
- ✅ **错误处理**: 完善的错误处理机制

## 快速开始

### 1. 启动服务

```bash
cd backend
python start_socket_agent.py
```

### 2. 访问测试页面

打开浏览器访问：`http://localhost:8000/test`

### 3. 连接测试

1. 输入用户ID (必需)
2. 点击"连接"按钮
3. 发送聊天消息
4. 观察 AI 流式响应

## API 端点

### WebSocket 端点

- **URL**: `ws://localhost:8000/ws`
- **参数**:
  - `user_id` (必需): 用户唯一标识
  - `username` (可选): 用户名
  - `room_id` (可选): 房间ID

### HTTP 端点

- **GET** `/` - 服务信息
- **GET** `/test` - 测试页面
- **GET** `/status` - 服务状态
- **POST** `/broadcast` - 广播消息

## 消息格式

### 发送消息 (客户端 -> 服务端)

```json
{
  "type": "chat",
  "content": "你好，今天天气怎么样？",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 接收消息 (服务端 -> 客户端)

```json
{
  "type": "ai_response",
  "content": {
    "conversation_id": "abc123",
    "current_agent": "Weather Agent",
    "messages": [
      {
        "content": "今天是晴天，气温25°C",
        "agent": "Weather Agent"
      }
    ],
    "events": [
      {
        "id": "event1",
        "type": "message",
        "agent": "Weather Agent",
        "content": "查询天气信息"
      }
    ],
    "context": {},
    "agents": [],
    "raw_response": "今天是晴天，气温25°C",
    "guardrails": []
  }
}
```

## 使用示例

### JavaScript 客户端

```javascript
// 连接 WebSocket
const ws = new WebSocket('ws://localhost:8000/ws?user_id=user123');

// 监听消息
ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    if (message.type === 'ai_response') {
        handleAIResponse(message.content);
    }
};

// 发送聊天消息
function sendChat(message) {
    ws.send(JSON.stringify({
        type: 'chat',
        content: message,
        timestamp: new Date().toISOString()
    }));
}

// 处理 AI 响应
function handleAIResponse(chatResponse) {
    console.log('当前代理:', chatResponse.current_agent);
    console.log('响应内容:', chatResponse.raw_response);
    console.log('消息列表:', chatResponse.messages);
    console.log('事件列表:', chatResponse.events);
}
```

### Python 客户端

```python
import asyncio
import websockets
import json

async def chat_client():
    uri = "ws://localhost:8000/ws?user_id=user123"
    
    async with websockets.connect(uri) as websocket:
        # 发送聊天消息
        await websocket.send(json.dumps({
            "type": "chat",
            "content": "你好，今天天气怎么样？",
            "timestamp": "2024-01-01T12:00:00Z"
        }))
        
        # 接收响应
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'ai_response':
                chat_response = data['content']
                print(f"AI 响应: {chat_response['raw_response']}")

# 运行客户端
asyncio.run(chat_client())
```

## 流式响应处理

流式响应会实时更新以下内容：

1. **raw_response**: 原始文本响应（逐步累积）
2. **current_agent**: 当前处理的代理
3. **messages**: 消息列表（逐步添加）
4. **events**: 事件列表（工具调用、代理切换等）

## 错误处理

服务端会发送以下错误类型：

- `INVALID_MESSAGE`: 消息格式无效
- `PARSE_ERROR`: JSON 解析错误
- `MESSAGE_PROCESSING_ERROR`: 消息处理错误
- `ai_error`: AI 处理错误

## 注意事项

1. **用户ID 必需**: 连接时必须提供用户ID
2. **房间隔离**: 每个用户有独立的房间
3. **流式更新**: 响应会实时更新，需要处理增量数据
4. **错误重试**: 建议实现重连机制

## 开发调试

### 启动调试模式

```bash
cd backend
python -m uvicorn main_socket_agent:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### 查看日志

服务会输出详细的日志信息，包括：
- WebSocket 连接状态
- 消息处理过程
- 流式响应事件
- 错误信息

### 测试建议

1. 使用多个浏览器标签页测试多用户场景
2. 测试不同类型的查询（天气、新闻、菜谱等）
3. 观察流式响应的实时更新
4. 测试错误情况下的处理

## 故障排除

### 常见问题

1. **连接失败**: 检查用户ID是否提供
2. **消息无响应**: 检查服务端日志是否有错误
3. **流式更新异常**: 检查 ChatResponse 格式是否正确

### 日志位置

服务日志会输出到控制台，包含以下信息：
- WebSocket 连接日志
- 消息处理日志
- 流式响应日志
- 错误详情

## 更新日志

- **v1.0.0**: 初始版本，支持基本的流式聊天功能
- 集成 main_stream.py 的流式处理逻辑
- 支持多代理流式响应
- 完善的错误处理机制 