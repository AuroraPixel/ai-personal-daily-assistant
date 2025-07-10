"""
通用HTTP客户端实现
"""

import requests
import time
from typing import Optional, Dict, Any


class APIClient:
    """通用API客户端，提供HTTP请求的基础功能"""
    
    def __init__(self, base_url: str, timeout: int = 10):
        """
        初始化API客户端
        
        Args:
            base_url: API的基础URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置默认headers
        self.session.headers.update({
            'User-Agent': 'Personal-Daily-Assistant/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None, 
                    method: str = 'GET', data: Optional[Dict] = None,
                    max_retries: int = 3) -> Optional[Dict[Any, Any]]:
        """
        发送HTTP请求
        
        Args:
            endpoint: API端点
            params: URL参数
            method: HTTP方法
            data: 请求体数据
            max_retries: 最大重试次数
            
        Returns:
            响应数据或None
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # 验证JSON响应
                try:
                    return response.json()
                except ValueError as e:
                    print(f"无效的JSON响应: {e}")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    
            except requests.exceptions.ConnectionError:
                print(f"连接错误 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # 请求限制
                    print(f"请求限制 (尝试 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(5)  # 等待更长时间
                else:
                    print(f"HTTP错误 {e.response.status_code}: {e}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"请求错误: {e}")
                return None
        
        print(f"经过 {max_retries} 次尝试后仍无法获取响应")
        return None
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[Any, Any]]:
        """GET请求快捷方法"""
        return self.make_request(endpoint, params=params, method='GET')
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[Any, Any]]:
        """POST请求快捷方法"""
        return self.make_request(endpoint, data=data, method='POST')
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[Any, Any]]:
        """PUT请求快捷方法"""
        return self.make_request(endpoint, data=data, method='PUT')
    
    def delete(self, endpoint: str) -> Optional[Dict[Any, Any]]:
        """DELETE请求快捷方法"""
        return self.make_request(endpoint, method='DELETE')
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close() 