#!/usr/bin/env python3
"""
AI 个人日常助手 WebSocket 客户端测试
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

class WebSocketClient:
    def __init__(self, user_id: str, username: str = None):
        self.user_id = user_id
        self.username = username
        self.uri = f"ws://localhost:8000/ws?user_id={user_id}"
        if username:
            self.uri += f"&username={username}"
        
    async def connect_and_test(self):
        """连接并测试 WebSocket"""
        try:
            print(f"🔗 正在连接到 {self.uri}")
            
            async with websockets.connect(self.uri) as websocket:
                print("✅ 连接成功!")
                
                # 启动消息监听任务
                listen_task = asyncio.create_task(self.listen_messages(websocket))
                
                # 发送测试消息
                await self.send_test_messages(websocket)
                
                # 等待监听任务完成
                await listen_task
                
        except ConnectionRefusedError:
            print("❌ 连接被拒绝，请确保服务器正在运行")
            print("   启动服务器: python start_socket_agent.py")
        except Exception as e:
            print(f"❌ 连接错误: {e}")
    
    async def listen_messages(self, websocket):
        """监听服务器消息"""
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("🔗 连接已关闭")
        except Exception as e:
            print(f"❌ 监听消息错误: {e}")
    
    async def handle_message(self, data):
        """处理接收到的消息"""
        message_type = data.get('type', 'unknown')
        content = data.get('content', {})
        
        print(f"\n📨 收到消息类型: {message_type}")
        
        if message_type == 'connect':
            print(f"🎉 {content.get('message', '连接成功')}")
            print(f"   房间ID: {content.get('room_id', 'N/A')}")
            
        elif message_type == 'ai_response':
            await self.handle_ai_response(content)
            
        elif message_type == 'ai_error':
            print(f"❌ AI 错误: {content.get('error', 'Unknown error')}")
            
        elif message_type == 'error':
            print(f"⚠️  系统错误: {content.get('error', 'Unknown error')}")
            
        else:
            print(f"📄 其他消息: {json.dumps(content, indent=2, ensure_ascii=False)}")
    
    async def handle_ai_response(self, content):
        """处理 AI 响应"""
        if isinstance(content, dict):
            if content.get('type') == 'completion':
                print("🎯 对话完成!")
                final_response = content.get('final_response', {})
                print(f"   对话ID: {final_response.get('conversation_id', 'N/A')}")
                print(f"   最终代理: {final_response.get('current_agent', 'N/A')}")
                print(f"   完整响应: {final_response.get('raw_response', 'N/A')}")
                print(f"   消息数量: {len(final_response.get('messages', []))}")
                print(f"   事件数量: {len(final_response.get('events', []))}")
            else:
                # 流式响应
                print(f"🤖 当前代理: {content.get('current_agent', 'N/A')}")
                print(f"📝 实时响应: {content.get('raw_response', 'N/A')}")
                
                messages = content.get('messages', [])
                if messages:
                    print(f"💬 消息 ({len(messages)}):")
                    for msg in messages[-3:]:  # 只显示最后3条
                        print(f"   [{msg.get('agent', 'N/A')}] {msg.get('content', 'N/A')}")
                
                events = content.get('events', [])
                if events:
                    print(f"⚡ 事件 ({len(events)}):")
                    for event in events[-3:]:  # 只显示最后3个
                        print(f"   [{event.get('type', 'N/A')}] {event.get('agent', 'N/A')}: {event.get('content', 'N/A')}")
        else:
            print(f"📄 AI 响应: {content}")
    
    async def send_test_messages(self, websocket):
        """发送测试消息"""
        test_messages = [
            "你好，我是用户测试",
            "今天天气怎么样？",
            "推荐一个简单的菜谱",
            "有什么最新的新闻吗？"
        ]
        
        for i, msg in enumerate(test_messages):
            print(f"\n📤 发送测试消息 {i+1}/{len(test_messages)}: {msg}")
            
            message = {
                "type": "chat",
                "content": msg,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(message))
            
            # 等待响应
            await asyncio.sleep(3)
        
        print("\n✅ 所有测试消息已发送")
        
        # 等待最后的响应
        await asyncio.sleep(5)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python test_websocket_client.py <user_id> [username]")
        print("示例: python test_websocket_client.py user123 张三")
        sys.exit(1)
    
    user_id = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("🧪 AI 个人日常助手 WebSocket 客户端测试")
    print(f"👤 用户ID: {user_id}")
    print(f"📝 用户名: {username or '未设置'}")
    print("-" * 50)
    
    client = WebSocketClient(user_id, username)
    
    try:
        asyncio.run(client.connect_and_test())
    except KeyboardInterrupt:
        print("\n👋 测试已中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    main() 