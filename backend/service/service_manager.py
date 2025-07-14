"""
全局服务管理器

统一管理数据库连接和服务实例，提高性能
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from threading import RLock
from core.database_core import DatabaseClient
from core.vector_core import ChromaVectorClient, VectorConfig
from core.auth_core.auth import AuthService


class ServiceManager:
    """全局服务管理器"""
    
    def __init__(self):
        self._lock = RLock()
        self._db_client: Optional[DatabaseClient] = None
        self._vector_client: Optional[ChromaVectorClient] = None
        self._auth_service: Optional[AuthService] = None
        self._services: Dict[str, Any] = {}
        
        # 用户信息缓存
        self._user_cache: Dict[str, Dict[str, Any]] = {}
        self._user_cache_expiry: Dict[str, datetime] = {}
        self._cache_duration = timedelta(minutes=15)  # 15分钟缓存
        
        # 令牌缓存
        self._token_cache: Dict[str, Dict[str, Any]] = {}
        self._token_cache_expiry: Dict[str, datetime] = {}
        
        # 连接池统计
        self._connection_pool_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "cached_tokens": 0,
            "cached_users": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        self._initialized = False
        self._logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """初始化服务管理器"""
        if self._initialized:
            return True
            
        with self._lock:
            try:
                # 初始化数据库客户端
                self._db_client = DatabaseClient()
                self._db_client.initialize()
                self._db_client.create_tables()
                
                # 初始化向量数据库客户端
                try:
                    config = VectorConfig.from_env()
                    self._vector_client = ChromaVectorClient(config)
                except Exception as e:
                    self._logger.warning(f"向量数据库初始化失败: {e}")
                    self._vector_client = None
                
                # 初始化认证服务
                self._auth_service = AuthService()
                
                self._initialized = True
                self._logger.info("服务管理器初始化成功")
                return True
                
            except Exception as e:
                self._logger.error(f"服务管理器初始化失败: {e}")
                return False
    
    def get_db_client(self) -> Optional[DatabaseClient]:
        """获取数据库客户端（单例）"""
        if not self._initialized:
            self.initialize()
        return self._db_client
    
    def get_vector_client(self) -> Optional[ChromaVectorClient]:
        """获取向量数据库客户端（单例）"""
        if not self._initialized:
            self.initialize()
        return self._vector_client
    
    def get_auth_service(self) -> Optional[AuthService]:
        """获取认证服务（单例）"""
        if not self._initialized:
            self.initialize()
        return self._auth_service
    
    def get_service(self, service_name: str, service_class=None, **kwargs):
        """获取服务实例（单例）"""
        if service_name not in self._services:
            if service_class is None:
                raise ValueError(f"服务 {service_name} 未注册且未提供服务类")
            
            with self._lock:
                if service_name not in self._services:
                    # 为服务传入共享的数据库客户端
                    if hasattr(service_class, '__init__'):
                        import inspect
                        sig = inspect.signature(service_class.__init__)
                        if 'db_client' in sig.parameters:
                            kwargs['db_client'] = self.get_db_client()
                        if 'vector_client' in sig.parameters:
                            kwargs['vector_client'] = self.get_vector_client()
                    
                    self._services[service_name] = service_class(**kwargs)
                    self._logger.info(f"创建服务实例: {service_name}")
        
        return self._services[service_name]
    
    def verify_token_cached(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌（带缓存）"""
        # 检查缓存
        if token in self._token_cache:
            if datetime.now() < self._token_cache_expiry[token]:
                self._connection_pool_stats["cache_hits"] += 1
                return self._token_cache[token]
            else:
                # 缓存过期，清理
                del self._token_cache[token]
                del self._token_cache_expiry[token]
                self._connection_pool_stats["cached_tokens"] = len(self._token_cache)
        
        # 缓存未命中
        self._connection_pool_stats["cache_misses"] += 1
        
        # 验证令牌
        auth_service = self.get_auth_service()
        if not auth_service:
            return None
        
        user_info = auth_service.verify_token(token)
        if user_info:
            # 缓存结果
            with self._lock:
                self._token_cache[token] = user_info
                self._token_cache_expiry[token] = datetime.now() + self._cache_duration
                self._connection_pool_stats["cached_tokens"] = len(self._token_cache)
        
        return user_info
    
    def get_user_cached(self, user_id: str, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取用户信息（带缓存）"""
        cache_key = f"user_{user_id}"
        
        # 检查缓存
        if cache_key in self._user_cache:
            if datetime.now() < self._user_cache_expiry[cache_key]:
                self._connection_pool_stats["cache_hits"] += 1
                return self._user_cache[cache_key]
            else:
                # 缓存过期，清理
                del self._user_cache[cache_key]
                del self._user_cache_expiry[cache_key]
                self._connection_pool_stats["cached_users"] = len(self._user_cache)
        
        # 缓存未命中
        self._connection_pool_stats["cache_misses"] += 1
        
        # 获取用户信息
        try:
            from service.services.user_service import UserService
            user_service = UserService()
            
            # 尝试通过用户名查找用户
            users = user_service.search_users_by_name(username) if username else []
            if not users and username:
                # 如果按名称找不到，尝试按邮箱查找
                users = user_service.search_users_by_email(username)
            
            if users:
                user = users[0]
                user_info = {
                    "user_id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "name": user.name
                }
                
                # 缓存结果
                with self._lock:
                    self._user_cache[cache_key] = user_info
                    self._user_cache_expiry[cache_key] = datetime.now() + self._cache_duration
                    self._connection_pool_stats["cached_users"] = len(self._user_cache)
                
                return user_info
            
        except Exception as e:
            self._logger.error(f"获取用户信息失败: {e}")
        
        return None
    
    def clear_cache(self):
        """清理所有缓存"""
        with self._lock:
            self._user_cache.clear()
            self._user_cache_expiry.clear()
            self._token_cache.clear()
            self._token_cache_expiry.clear()
            self._logger.info("已清理所有缓存")
    
    def clear_expired_cache(self):
        """清理过期缓存"""
        now = datetime.now()
        
        with self._lock:
            # 清理过期的用户缓存
            expired_users = [k for k, v in self._user_cache_expiry.items() if now >= v]
            for key in expired_users:
                del self._user_cache[key]
                del self._user_cache_expiry[key]
            
            # 清理过期的令牌缓存
            expired_tokens = [k for k, v in self._token_cache_expiry.items() if now >= v]
            for key in expired_tokens:
                del self._token_cache[key]
                del self._token_cache_expiry[key]
            
            if expired_users or expired_tokens:
                self._logger.info(f"清理过期缓存: {len(expired_users)} 个用户, {len(expired_tokens)} 个令牌")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取服务管理器统计信息"""
        # 更新实时统计
        self._connection_pool_stats["cached_users"] = len(self._user_cache)
        self._connection_pool_stats["cached_tokens"] = len(self._token_cache)
        
        return {
            "initialized": self._initialized,
            "db_client_active": self._db_client is not None,
            "vector_client_active": self._vector_client is not None,
            "services_count": len(self._services),
            "user_cache_size": len(self._user_cache),
            "token_cache_size": len(self._token_cache),
            "connection_pool_stats": self._connection_pool_stats.copy()
        }
    
    def close(self):
        """关闭服务管理器"""
        with self._lock:
            # 关闭数据库连接
            if self._db_client:
                try:
                    self._db_client.close()
                    self._logger.info("数据库连接已关闭")
                except Exception as e:
                    self._logger.error(f"关闭数据库连接失败: {e}")
            
            # 关闭向量数据库连接
            if self._vector_client:
                try:
                    # 尝试关闭，如果没有close方法则忽略
                    if hasattr(self._vector_client, 'close'):
                        getattr(self._vector_client, 'close')()
                    self._logger.info("向量数据库连接已关闭")
                except Exception as e:
                    self._logger.error(f"关闭向量数据库连接失败: {e}")
            
            # 清理缓存
            self.clear_cache()
            
            # 清理服务实例
            self._services.clear()
            
            self._initialized = False
            self._logger.info("服务管理器已关闭")


# 全局服务管理器实例
service_manager = ServiceManager() 