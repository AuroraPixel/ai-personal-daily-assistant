"""
智能体会话管理模块

管理单个会话的状态和消息历史，提供数据库持久化和内存缓存功能
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import sys
from pathlib import Path

# 添加后端目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from core.database_core import DatabaseClient
from service.services.conversation_service import ConversationService
from service.services.chat_message_service import ChatMessageService
from service.models.chat_message import ChatMessage
from service.models.conversation import Conversation


class AgentSession:
    """
    智能体会话管理类
    
    管理单个会话的状态和消息历史，提供数据库持久化和内存缓存功能
    """
    
    def __init__(self, conversation_id_str: str, user_id: int, db_client: DatabaseClient, max_messages: int = 100):
        """
        初始化会话管理器
        
        Args:
            conversation_id_str: 会话UUID字符串
            user_id: 用户ID
            max_messages: 最大缓存消息数量
        """
        self.conversation_id_str = conversation_id_str
        self.user_id = user_id
        self.max_messages = max_messages
        
        # 数据库服务
        self.db_client = db_client
        self.conversation_service = ConversationService(self.db_client)
        self.chat_message_service = ChatMessageService(self.db_client)
        
        # 内存缓存
        self._message_cache: List[ChatMessage] = []
        self._conversation: Optional[Conversation] = None
        self._state: Dict[str, Any] = {}
        
        # 初始化状态
        self._initialized = False
        self._closed = False
    
    async def initialize(self, conversation_title: str = "New Conversation") -> bool:
        """
        初始化会话管理器
        
        Args:
            conversation_title: 会话标题（仅在创建新会话时使用）
            
        Returns:
            初始化是否成功
        """
        try:
            # 确保数据库初始化
            if not self.db_client._initialized:
                self.db_client.initialize()
            
            # 尝试获取现有会话
            self._conversation = self.conversation_service.get_conversation_by_id_str(self.conversation_id_str)
            
            # 如果会话不存在，创建新会话
            if self._conversation is None:
                self._conversation = await self._create_new_conversation(conversation_title)
                if self._conversation is None:
                    return False
            
            # 加载历史消息到缓存
            await self._load_messages_to_cache()
            
            # 构建初始状态
            self._build_initial_state()
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"初始化会话管理器失败: {e}")
            return False
    
    async def _create_new_conversation(self, title: str) -> Optional[Conversation]:
        """
        创建新会话
        
        Args:
            title: 会话标题
            
        Returns:
            创建的会话对象
        """
        try:
            conversation = self.conversation_service.create_conversation(
                user_id=self.user_id,
                title=title,
                description=f"智能体会话 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                status=Conversation.STATUS_ACTIVE,
                id_str=self.conversation_id_str
            )
            return conversation
            
        except Exception as e:
            print(f"创建会话失败: {e}")
            return None
    
    async def _load_messages_to_cache(self):
        """
        从数据库加载历史消息到缓存
        倒序读取指定数量，然后正序排序
        """
        try:
            # 从数据库获取最新的消息（倒序）
            messages = self.chat_message_service.get_conversation_messages_by_id_str(
                conversation_id_str=self.conversation_id_str,
                limit=self.max_messages,
                offset=0,
                order_desc=True
            )
            
            # 正序排序（最老的在前面）
            messages.reverse()
            
            # 缓存消息
            self._message_cache = messages
            
        except Exception as e:
            print(f"加载消息缓存失败: {e}")
            self._message_cache = []
    
    def _build_initial_state(self):
        """
        构建初始状态，兼容main.py的格式
        """
        # 转换消息格式
        input_items = []
        for msg in self._message_cache:
            # 转换为main.py兼容的格式
            role = self._convert_sender_type_to_role(str(msg.sender_type))
            input_items.append({
                "content": str(msg.content),
                "role": role
            })
        
        # 构建状态
        self._state = {
            "input_items": input_items,
            "context": None,  # 会由上层设置
            "current_agent": "Triage Agent"  # 默认智能体
        }
    
    def _convert_sender_type_to_role(self, sender_type: str) -> str:
        """
        转换发送者类型到角色
        
        Args:
            sender_type: 数据库中的发送者类型
            
        Returns:
            main.py兼容的角色
        """
        mapping = {
            ChatMessage.SENDER_TYPE_HUMAN: "user",
            ChatMessage.SENDER_TYPE_AI: "assistant",
            ChatMessage.SENDER_TYPE_TOOL: "assistant",
            ChatMessage.SENDER_TYPE_SYSTEM: "system"
        }
        return mapping.get(sender_type, "user")
    
    def _convert_role_to_sender_type(self, role: str) -> str:
        """
        转换角色到发送者类型
        
        Args:
            role: main.py中的角色
            
        Returns:
            数据库中的发送者类型
        """
        mapping = {
            "user": ChatMessage.SENDER_TYPE_HUMAN,
            "assistant": ChatMessage.SENDER_TYPE_AI,
            "system": ChatMessage.SENDER_TYPE_SYSTEM
        }
        return mapping.get(role, ChatMessage.SENDER_TYPE_HUMAN)
    
    def get_state(self) -> Dict[str, Any]:
        """
        获取会话状态
        
        Returns:
            兼容main.py的状态字典
        """
        if not self._initialized:
            raise RuntimeError("会话管理器未初始化")
        
        return self._state.copy()
    
    def set_context(self, context: Any):
        """
        设置会话上下文
        
        Args:
            context: PersonalAssistantContext对象
        """
        if not self._initialized:
            raise RuntimeError("会话管理器未初始化")
        
        self._state["context"] = context
    
    def set_current_agent(self, agent_name: str):
        """
        设置当前智能体
        
        Args:
            agent_name: 智能体名称
        """
        if not self._initialized:
            raise RuntimeError("会话管理器未初始化")
        
        self._state["current_agent"] = agent_name
    
    async def save_message(self, content: str, role: str, sender_id: Optional[str] = None, 
                          extra_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存消息到数据库和缓存
        
        Args:
            content: 消息内容
            role: 消息角色 (user/assistant/system)
            sender_id: 发送者ID（可选）
            extra_data: 额外数据（可选）
            
        Returns:
            保存是否成功
        """
        if not self._initialized:
            raise RuntimeError("会话管理器未初始化")
        
        try:
            # 转换角色到发送者类型
            sender_type = self._convert_role_to_sender_type(role)
            
            # 准备额外数据
            extra_data_str = None
            if extra_data:
                extra_data_str = json.dumps(extra_data, ensure_ascii=False)
            
            # 保存到数据库
            message = self.chat_message_service.create_message_by_id_str(
                conversation_id_str=self.conversation_id_str,
                sender_type=sender_type,
                content=content,
                sender_id=sender_id,
                message_type='text',
                extra_data=extra_data_str
            )
            
            if message is None:
                return False
            
            # 添加到缓存
            self._message_cache.append(message)
            
            # 维护缓存大小
            if len(self._message_cache) > self.max_messages:
                self._message_cache = self._message_cache[-self.max_messages:]
            
            # 更新状态
            self._state["input_items"].append({
                "content": str(content),
                "role": str(role)
            })
            
            # 维护状态中的消息数量
            if len(self._state["input_items"]) > self.max_messages:
                self._state["input_items"] = self._state["input_items"][-self.max_messages:]
            
            return True
            
        except Exception as e:
            print(f"保存消息失败: {e}")
            return False
    
    async def save_state(self, state: Dict[str, Any]) -> bool:
        """
        保存完整状态
        
        Args:
            state: 兼容main.py的状态字典
            
        Returns:
            保存是否成功
        """
        if not self._initialized:
            raise RuntimeError("会话管理器未初始化")
        
        try:
            # 更新当前状态
            self._state.update(state)
            
            # 如果有新的input_items，需要将新消息保存到数据库
            input_items = state.get("input_items", [])
            cached_count = len(self._message_cache)
            
            # 保存新消息
            for i, item in enumerate(input_items):
                if i >= cached_count:
                    # 这是新消息
                    await self.save_message(
                        content=item["content"],
                        role=item["role"]
                    )
            
            return True
            
        except Exception as e:
            print(f"保存状态失败: {e}")
            return False
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的消息
        
        Args:
            limit: 返回数量限制
            
        Returns:
            消息列表
        """
        if not self._initialized:
            raise RuntimeError("会话管理器未初始化")
        
        recent_items = self._state["input_items"][-limit:]
        return recent_items
    
    def get_conversation_info(self) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        Returns:
            会话信息字典
        """
        if not self._initialized or not self._conversation:
            return None
        
        return {
            "id": self._conversation.id,
            "id_str": self._conversation.id_str,
            "user_id": self._conversation.user_id,
            "title": self._conversation.title,
            "description": self._conversation.description,
            "status": self._conversation.status,
            "message_count": len(self._message_cache),
            "last_active": self._conversation.last_active,
            "created_at": self._conversation.created_at
        }
    
    async def update_conversation_title(self, title: str) -> bool:
        """
        更新会话标题
        
        Args:
            title: 新标题
            
        Returns:
            更新是否成功
        """
        if not self._initialized or not self._conversation:
            return False
        
        try:
            updated_conversation = self.conversation_service.update_conversation_by_id_str(
                conversation_id_str=self.conversation_id_str,
                title=title
            )
            
            if updated_conversation:
                self._conversation = updated_conversation
                return True
            
            return False
            
        except Exception as e:
            print(f"更新会话标题失败: {e}")
            return False
    
    def clear_cache(self):
        """
        清空内存缓存
        """
        self._message_cache.clear()
        self._state = {
            "input_items": [],
            "context": None,
            "current_agent": "Triage Agent"
        }
    
    def close(self):
        """
        关闭会话管理器，释放资源
        """
        if self._closed:
            return
        
        try:
            # 清空缓存
            self.clear_cache()
            
            # 关闭数据库连接
            if self.conversation_service:
                self.conversation_service.close()
            if self.chat_message_service:
                self.chat_message_service.close()
            if self.db_client:
                self.db_client.close()
            
            self._closed = True
            self._initialized = False
            
        except Exception as e:
            print(f"关闭会话管理器失败: {e}")
    
    def __del__(self):
        """
        析构函数，确保资源释放
        """
        if not self._closed:
            self.close()
    
    def __enter__(self):
        """
        上下文管理器入口
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        """
        self.close()


class AgentSessionManager:
    """
    智能体会话管理器
    
    替代main.py中的InMemoryConversationStore，提供数据库持久化功能
    """
    
    def __init__(self, default_user_id: int = 1, max_messages: int = 100):
        """
        初始化会话管理器
        
        Args:
            default_user_id: 默认用户ID
            max_messages: 每个会话的最大消息数量
        """
        self.default_user_id = default_user_id
        self.max_messages = max_messages
        self._sessions: Dict[str, AgentSession] = {}
        self._closed = False
    
    async def get_session(self, conversation_id: str) -> Optional[AgentSession]:
        """
        获取或创建会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            会话对象
        """
        if self._closed:
            raise RuntimeError("会话管理器已关闭")
        
        # 如果会话已存在，直接返回
        if conversation_id in self._sessions:
            return self._sessions[conversation_id]
        
        # 创建新会话
        session = AgentSession(
            conversation_id_str=conversation_id,
            user_id=self.default_user_id,
            max_messages=self.max_messages
        )
        
        # 初始化会话
        success = await session.initialize()
        if not success:
            return None
        
        # 缓存会话
        self._sessions[conversation_id] = session
        return session
    
    async def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话状态（兼容main.py的ConversationStore接口）
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            会话状态字典
        """
        try:
            session = await self.get_session(conversation_id)
            if session is None:
                return None
            
            return session.get_state()
            
        except Exception as e:
            print(f"获取会话状态失败: {e}")
            return None
    
    async def save(self, conversation_id: str, state: Dict[str, Any]) -> bool:
        """
        保存会话状态（兼容main.py的ConversationStore接口）
        
        Args:
            conversation_id: 会话ID
            state: 会话状态字典
            
        Returns:
            保存是否成功
        """
        try:
            session = await self.get_session(conversation_id)
            if session is None:
                return False
            
            # 设置上下文和当前智能体
            if "context" in state:
                session.set_context(state["context"])
            if "current_agent" in state:
                session.set_current_agent(state["current_agent"])
            
            # 保存状态
            return await session.save_state(state)
            
        except Exception as e:
            print(f"保存会话状态失败: {e}")
            return False
    
    async def create_conversation(self, conversation_id: str, title: str = "New Conversation") -> bool:
        """
        创建新会话
        
        Args:
            conversation_id: 会话ID
            title: 会话标题
            
        Returns:
            创建是否成功
        """
        try:
            if conversation_id in self._sessions:
                return True  # 会话已存在
            
            session = AgentSession(
                conversation_id_str=conversation_id,
                user_id=self.default_user_id,
                max_messages=self.max_messages
            )
            
            success = await session.initialize(title)
            if success:
                self._sessions[conversation_id] = session
                return True
            
            return False
            
        except Exception as e:
            print(f"创建会话失败: {e}")
            return False
    
    def get_conversation_info(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            会话信息字典
        """
        if conversation_id not in self._sessions:
            return None
        
        session = self._sessions[conversation_id]
        return session.get_conversation_info()
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        列出所有会话
        
        Returns:
            会话信息列表
        """
        conversations = []
        for conversation_id, session in self._sessions.items():
            info = session.get_conversation_info()
            if info:
                conversations.append(info)
        
        return conversations
    
    async def remove_conversation(self, conversation_id: str) -> bool:
        """
        移除会话
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            移除是否成功
        """
        try:
            if conversation_id in self._sessions:
                session = self._sessions[conversation_id]
                session.close()
                del self._sessions[conversation_id]
            
            return True
            
        except Exception as e:
            print(f"移除会话失败: {e}")
            return False
    
    def close(self):
        """
        关闭会话管理器，释放所有资源
        """
        if self._closed:
            return
        
        try:
            # 关闭所有会话
            for session in self._sessions.values():
                session.close()
            
            self._sessions.clear()
            self._closed = True
            
        except Exception as e:
            print(f"关闭会话管理器失败: {e}")
    
    def __del__(self):
        """
        析构函数，确保资源释放
        """
        if not self._closed:
            self.close()
    
    def __enter__(self):
        """
        上下文管理器入口
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        """
        self.close()


# 创建一个同步包装器类，用于与main.py的现有代码兼容
class SyncAgentSessionManager:
    """
    同步会话管理器包装器
    
    为了与main.py的现有代码兼容，提供同步接口
    """
    
    def __init__(self, default_user_id: int = 1, max_messages: int = 100):
        """
        初始化同步会话管理器
        
        Args:
            default_user_id: 默认用户ID
            max_messages: 每个会话的最大消息数量
        """
        self.async_manager = AgentSessionManager(default_user_id, max_messages)
        self._loop = None
    
    def _run_async(self, coro):
        """
        运行异步函数
        
        Args:
            coro: 协程对象
            
        Returns:
            协程结果
        """
        import asyncio
        
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用 run_until_complete
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                # 如果事件循环不在运行，直接运行
                return loop.run_until_complete(coro)
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            return asyncio.run(coro)
    
    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话状态（同步版本）
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            会话状态字典
        """
        return self._run_async(self.async_manager.get(conversation_id))
    
    def save(self, conversation_id: str, state: Dict[str, Any]) -> bool:
        """
        保存会话状态（同步版本）
        
        Args:
            conversation_id: 会话ID
            state: 会话状态字典
            
        Returns:
            保存是否成功
        """
        return self._run_async(self.async_manager.save(conversation_id, state))
    
    def create_conversation(self, conversation_id: str, title: str = "New Conversation") -> bool:
        """
        创建新会话（同步版本）
        
        Args:
            conversation_id: 会话ID
            title: 会话标题
            
        Returns:
            创建是否成功
        """
        return self._run_async(self.async_manager.create_conversation(conversation_id, title))
    
    def get_conversation_info(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息（同步版本）
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            会话信息字典
        """
        return self.async_manager.get_conversation_info(conversation_id)
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        列出所有会话（同步版本）
        
        Returns:
            会话信息列表
        """
        return self.async_manager.list_conversations()
    
    def remove_conversation(self, conversation_id: str) -> bool:
        """
        移除会话（同步版本）
        
        Args:
            conversation_id: 会话ID
            
        Returns:
            移除是否成功
        """
        return self._run_async(self.async_manager.remove_conversation(conversation_id))
    
    def close(self):
        """
        关闭会话管理器
        """
        self.async_manager.close()
    
    def __del__(self):
        """
        析构函数
        """
        self.async_manager.close()
    
    def __enter__(self):
        """
        上下文管理器入口
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        """
        self.close()


"""
使用示例和集成说明
==================

1. 基本使用示例：

```python
# 创建会话管理器
async def example_usage():
    # 异步版本
    async with AgentSessionManager(default_user_id=1, max_messages=100) as manager:
        # 获取或创建会话
        session = await manager.get_session("conversation_123")
        
        # 保存消息
        await session.save_message("Hello", "user")
        await session.save_message("Hi there!", "assistant")
        
        # 获取会话状态
        state = session.get_state()
        print(f"Messages: {state['input_items']}")
        
        # 获取会话信息
        info = session.get_conversation_info()
        print(f"Conversation: {info['title']}")

# 同步版本
with SyncAgentSessionManager(default_user_id=1, max_messages=100) as manager:
    # 创建会话
    manager.create_conversation("conversation_123", "测试会话")
    
    # 获取会话状态
    state = manager.get("conversation_123")
    if state:
        print(f"Messages: {state['input_items']}")
    
    # 保存状态
    new_state = {
        "input_items": [
            {"content": "Hello", "role": "user"},
            {"content": "Hi there!", "role": "assistant"}
        ],
        "current_agent": "Triage Agent"
    }
    success = manager.save("conversation_123", new_state)
    print(f"Save success: {success}")
```

2. 集成到 main.py：

在 backend/main.py 中，替换现有的会话存储：

```python
# 原有代码：
# conversation_store = InMemoryConversationStore()

# 替换为：
from agent.agent_session import SyncAgentSessionManager
conversation_store = SyncAgentSessionManager(default_user_id=1, max_messages=100)
```

这样就能无缝集成到现有系统中，并获得以下好处：

- 数据库持久化：会话和消息会保存到数据库
- 内存缓存：提高性能，避免频繁数据库查询
- 消息数量限制：控制内存使用
- 自动清理：防止内存泄露
- 完全兼容：与现有 main.py 代码完全兼容

3. 配置选项：

```python
# 自定义配置
conversation_store = SyncAgentSessionManager(
    default_user_id=1,          # 默认用户ID
    max_messages=200            # 每个会话最大消息数量
)
```

4. 高级功能：

```python
# 获取会话信息
info = conversation_store.get_conversation_info("conversation_123")
if info:
    print(f"标题: {info['title']}")
    print(f"消息数量: {info['message_count']}")
    print(f"最后活跃: {info['last_active']}")

# 列出所有会话
conversations = conversation_store.list_conversations()
for conv in conversations:
    print(f"会话 {conv['id_str']}: {conv['title']}")

# 移除会话
conversation_store.remove_conversation("conversation_123")
```

注意事项：
- 确保数据库已正确初始化
- 在应用关闭时调用 conversation_store.close() 释放资源
- 数据库连接失败时会自动降级为基本功能
- 支持多用户，但当前默认使用单一用户ID
"""
