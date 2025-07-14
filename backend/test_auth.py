#!/usr/bin/env python3
"""
认证功能测试脚本

测试JWT认证、登录、API保护等功能
"""

import asyncio
import json
import requests
import websockets
from datetime import datetime
from typing import Dict, Any, Optional

# 测试配置
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

class AuthTester:
    """认证功能测试类"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token = None
        self.user_info = None
        
    def test_login(self, username: str = "Leanne Graham", password: str = "admin123456") -> bool:
        """测试登录功能"""
        print(f"=== 测试登录功能 ===")
        
        try:
            # 发送登录请求
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={
                    "username": username,
                    "password": password
                }
            )
            
            print(f"登录响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"登录响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if data.get("success"):
                    self.access_token = data.get("token", {}).get("access_token")
                    self.user_info = data.get("user_info")
                    
                    # 检查Cookie是否设置
                    cookies = response.cookies
                    if "access_token" in cookies:
                        print("✅ Cookie设置成功")
                    else:
                        print("⚠️  Cookie未设置")
                    
                    print("✅ 登录成功")
                    return True
                else:
                    print(f"❌ 登录失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 登录请求失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_wrong_password(self) -> bool:
        """测试错误密码"""
        print(f"\n=== 测试错误密码 ===")
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={
                    "username": "Leanne Graham",
                    "password": "wrongpassword"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("success"):
                    print("✅ 错误密码正确被拒绝")
                    return True
                else:
                    print("❌ 错误密码错误被接受")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_protected_api(self) -> bool:
        """测试受保护的API"""
        print(f"\n=== 测试受保护的API ===")
        
        if not self.access_token or not self.user_info:
            print("❌ 需要先登录")
            return False
        
        try:
            # 测试用户信息接口
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.base_url}/auth/me", headers=headers)
            
            print(f"获取用户信息响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"用户信息: {json.dumps(data, indent=2, ensure_ascii=False)}")
                print("✅ 受保护API访问成功")
                return True
            else:
                print(f"❌ 受保护API访问失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_api_without_token(self) -> bool:
        """测试无令牌访问受保护API"""
        print(f"\n=== 测试无令牌访问受保护API ===")
        
        try:
            response = requests.get(f"{self.base_url}/auth/me")
            
            if response.status_code == 401:
                print("✅ 无令牌访问正确被拒绝")
                return True
            else:
                print(f"❌ 无令牌访问应该返回401，但返回了: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_conversation_api(self) -> bool:
        """测试会话API的认证保护"""
        print(f"\n=== 测试会话API的认证保护 ===")
        
        if not self.access_token or not self.user_info:
            print("❌ 需要先登录")
            return False
        
        try:
            user_id = self.user_info.get("user_id")
            if not user_id:
                print("❌ 无法获取用户ID")
                return False
            
            # 测试会话列表接口
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.base_url}/api/conversations/{user_id}", headers=headers)
            
            print(f"会话列表响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"会话列表: {json.dumps(data, indent=2, ensure_ascii=False)}")
                print("✅ 会话API访问成功")
                return True
            else:
                print(f"❌ 会话API访问失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_other_user_access(self) -> bool:
        """测试访问其他用户的数据"""
        print(f"\n=== 测试访问其他用户的数据 ===")
        
        if not self.access_token:
            print("❌ 需要先登录")
            return False
        
        try:
            # 尝试访问其他用户的会话
            other_user_id = "999"  # 假设一个不存在的用户ID
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.base_url}/api/conversations/{other_user_id}", headers=headers)
            
            if response.status_code == 403:
                print("✅ 访问其他用户数据正确被拒绝")
                return True
            else:
                print(f"❌ 访问其他用户数据应该返回403，但返回了: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    async def test_websocket_auth(self) -> bool:
        """测试WebSocket认证"""
        print(f"\n=== 测试WebSocket认证 ===")
        
        if not self.access_token or not self.user_info:
            print("❌ 需要先登录")
            return False
        
        try:
            user_id = self.user_info.get("user_id")
            username = self.user_info.get("username")
            
            # 测试带令牌的WebSocket连接
            ws_url = f"{WS_URL}?user_id={user_id}&username={username}&token={self.access_token}"
            
            websocket = await websockets.connect(ws_url)
            try:
                print("✅ WebSocket连接成功")
                
                # 接收欢迎消息
                welcome_message = await asyncio.wait_for(websocket.recv(), timeout=5)
                welcome_data = json.loads(welcome_message)
                print(f"欢迎消息: {json.dumps(welcome_data, indent=2, ensure_ascii=False)}")
                
                # 检查是否标记为已认证
                if welcome_data.get("content", {}).get("authenticated"):
                    print("✅ WebSocket认证成功")
                    return True
                else:
                    print("❌ WebSocket认证失败")
                    return False
            finally:
                await websocket.close()
                    
        except Exception as e:
            print(f"❌ WebSocket测试异常: {e}")
            return False
    
    def test_logout(self) -> bool:
        """测试退出登录"""
        print(f"\n=== 测试退出登录 ===")
        
        if not self.access_token:
            print("❌ 需要先登录")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.post(f"{self.base_url}/auth/logout", headers=headers)
            
            print(f"退出登录响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"退出登录响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if data.get("success"):
                    print("✅ 退出登录成功")
                    self.access_token = None
                    self.user_info = None
                    return True
                else:
                    print("❌ 退出登录失败")
                    return False
            else:
                print(f"❌ 退出登录请求失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False


async def run_tests():
    """运行所有测试"""
    print("🧪 AI 个人日常助手认证功能测试")
    print("=" * 50)
    
    tester = AuthTester()
    
    # 测试项目列表
    tests = [
        ("登录功能", tester.test_login),
        ("错误密码", tester.test_wrong_password),
        ("受保护API", tester.test_protected_api),
        ("无令牌访问", tester.test_api_without_token),
        ("会话API", tester.test_conversation_api),
        ("其他用户访问", tester.test_other_user_access),
        ("WebSocket认证", tester.test_websocket_auth),
        ("退出登录", tester.test_logout),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n🔍 运行测试: {name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                print(f"✅ 测试通过: {name}")
                passed += 1
            else:
                print(f"❌ 测试失败: {name}")
                failed += 1
                
        except Exception as e:
            print(f"💥 测试异常: {name} - {e}")
            failed += 1
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！认证功能工作正常。")
    else:
        print("⚠️  部分测试失败，请检查认证功能实现。")
    
    return failed == 0


if __name__ == "__main__":
    """
    运行测试前，请确保：
    1. 服务器正在运行 (python backend/main_socket_agent.py)
    2. 数据库已正确配置
    3. 依赖已安装 (pip install -r requirements.txt)
    """
    
    try:
        success = asyncio.run(run_tests())
        if success:
            print("\n✅ 所有测试通过！")
        else:
            print("\n❌ 部分测试失败！")
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n测试运行时发生错误: {e}") 