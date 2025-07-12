from __future__ import annotations as _annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Add backend directory to Python path FIRST
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Now import project modules
from agents.model_settings import ModelSettings
from agents.extensions.models.litellm_model import LitellmModel
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.mcp import ToolFilterContext
from service.models.todo import Todo

# Import services
from service.services.user_service import UserService
from service.services.preference_service import PreferenceService
from service.services.todo_service import TodoService
from core.database_core import DatabaseClient
from core.vector_core.client import ChromaVectorClient

from agents import (
    Agent,
    RunContextWrapper,
    set_tracing_disabled,
    Runner,
    TResponseInputItem,
    function_tool,
    handoff,
    GuardrailFunctionOutput,
    input_guardrail,
    InputGuardrailTripwireTriggered,
    MessageOutputItem,
    HandoffOutputItem,
    ItemHelpers,
    Handoff,
    ToolCallItem,
    ToolCallOutputItem,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


class PersonalAssistantContext(BaseModel):
    """个人助手上下文数据模型"""
    model_config = {
        "arbitrary_types_allowed": True,
        "from_attributes": True
    }
    
    user_id: int  # 用户ID
    user_name: str  # 用户姓名
    lat: str  # 纬度
    lng: str  # 经度
    user_preferences: Dict[str, Dict[str, Any]]  # 用户偏好
    todos: List[Todo]  # 待办事项
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """重写序列化方法，确保Todo对象可以被正确序列化"""
        from datetime import datetime
        
        data = super().model_dump(**kwargs)
        
        # 将Todo对象转换为字典
        if 'todos' in data and data['todos']:
            serialized_todos = []
            for todo in self.todos:
                if hasattr(todo, 'to_dict'):
                    todo_dict = todo.to_dict()
                else:
                    todo_dict = {
                        'id': getattr(todo, 'id', None),
                        'user_id': getattr(todo, 'user_id', None),
                        'title': getattr(todo, 'title', ''),
                        'description': getattr(todo, 'description', ''),
                        'completed': getattr(todo, 'completed', False),
                        'priority': getattr(todo, 'priority', 'medium'),
                        'due_date': getattr(todo, 'due_date', None),
                        'completed_at': getattr(todo, 'completed_at', None),
                        'created_at': getattr(todo, 'created_at', None),
                        'updated_at': getattr(todo, 'updated_at', None),
                    }
                
                # 转换datetime对象为ISO字符串
                for key, value in todo_dict.items():
                    if isinstance(value, datetime):
                        todo_dict[key] = value.isoformat()
                
                serialized_todos.append(todo_dict)
            
            data['todos'] = serialized_todos
        
        return data


class PersonalAssistantManager:
    """个人助手管理器类 - 统一管理所有智能体和相关功能"""
    
    def __init__(self, db_client: DatabaseClient, mcp_server_url: str = "http://127.0.0.1:8002/mcp"):
        """
        初始化个人助手管理器
        
        Args:
            db_client: 数据库客户端（从外部传入）
            mcp_server_url: MCP服务器URL地址
        """
        # 加载环境变量
        load_dotenv()
        set_tracing_disabled(disabled=True)
        
        # 核心组件
        self.db_client = db_client
        self.vector_client = None
        self.mcp_server_url = mcp_server_url
        
        # 模型配置
        self.model = self._create_model()
        self.model_settings = self._create_model_settings()
        
        # MCP服务器
        self.mcp_server = self._create_mcp_server()
        
        # 智能体
        self.agents = {}
        
        # 初始化状态
        self._initialized = False
        
        print("🤖 个人助手管理器已创建")
    
    def _create_model(self) -> LitellmModel:
        """创建语言模型"""
        return LitellmModel(
            model="gpt-4o",
            base_url=os.getenv("CUSTOMIZE_OPENAI_API_BASE_URL"),
            api_key=os.getenv("CUSTOMIZE_OPENAI_API_KEY"),
        )
    
    def _create_model_settings(self) -> ModelSettings:
        """创建模型设置"""
        return ModelSettings(
            temperature=0.6,  # 控制创造性
            top_p=0.9,  # 词汇多样性
            tool_choice="auto",  # 自动选择工具
            parallel_tool_calls=True,  # 并行调用工具
            truncation="auto",  # 截断策略
        )
    
    def _create_mcp_server(self) -> MCPServerStreamableHttp:
        """创建MCP服务器连接"""
        return MCPServerStreamableHttp(
            name="personal_assistant_tools",
            params={"url": self.mcp_server_url},
            tool_filter=self._tool_filter
        )
    
    def _tool_filter(self, context: ToolFilterContext, tool) -> bool:
        """工具过滤器 - 根据智能体类型过滤可用工具"""
        agent_name = context.agent.name
        
        tool_mapping = {
            "Weather Agent": "weather_",
            "News Agent": "news_",
            "Recipe Agent": "recipe_",
            "Personal Assistant Agent": "user_",
        }
        
        prefix = tool_mapping.get(agent_name)
        return bool(prefix and tool.name.startswith(prefix))
    
    async def initialize(self) -> bool:
        """初始化所有服务和智能体"""
        try:
            print("🚀 开始初始化个人助手管理器...")
            
            # 1. 初始化MCP服务器
            await self._initialize_mcp_server()
            
            # 2. 初始化向量数据库
            self._initialize_vector_database()
            
            # 3. 初始化所有智能体
            self._initialize_agents()
            
            # 4. 设置智能体关系
            self._setup_agent_relationships()
            
            self._initialized = True
            print("🎉 个人助手管理器初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    async def _initialize_mcp_server(self) -> bool:
        """初始化MCP服务器连接"""
        try:
            print("🔌 正在连接MCP服务器...")
            await self.mcp_server.connect()
            print(f"✅ MCP服务器连接成功: {self.mcp_server.name}")
            return True
        except Exception as e:
            print(f"❌ MCP服务器连接失败: {e}")
            print(f"   服务器地址: {self.mcp_server_url}")
            print("⚠️  将在没有MCP服务器的情况下继续运行")
            return False
    
    def _initialize_vector_database(self) -> bool:
        """初始化向量数据库"""
        try:
            print("🗂️  正在初始化向量数据库...")
            self.vector_client = ChromaVectorClient()
            print("✅ 向量数据库初始化成功")
            return True
        except Exception as e:
            print(f"❌ 向量数据库初始化失败: {e}")
            print("⚠️  将在没有向量数据库的情况下继续运行")
            return False
    
    def _initialize_agents(self):
        """初始化所有智能体"""
        print("🤖 正在创建智能体...")
        
        # 天气智能体
        self.agents['weather'] = Agent[PersonalAssistantContext](
            name="Weather Agent",
            model=self.model,
            model_settings=self.model_settings,
            handoff_description="A weather agent that can get the weather of a location.",
            instructions=self._get_weather_instructions,
            mcp_servers=[self.mcp_server],
        )
        
        # 新闻智能体
        self.agents['news'] = Agent[PersonalAssistantContext](
            name="News Agent",
            model=self.model,
            model_settings=self.model_settings,
            handoff_description="A news agent that can get the news of a location.",
            instructions=self._get_news_instructions,
            mcp_servers=[self.mcp_server],
        )
        
        # 菜谱智能体
        self.agents['recipe'] = Agent[PersonalAssistantContext](
            name="Recipe Agent",
            model=self.model,
            model_settings=self.model_settings,
            handoff_description="A recipe agent that can get the recipe of a location.",
            instructions=self._get_recipe_instructions,
            mcp_servers=[self.mcp_server],
        )
        
        # 个人助手智能体
        self.agents['personal'] = Agent[PersonalAssistantContext](
            name="Personal Assistant Agent",
            model=self.model,
            model_settings=self.model_settings,
            handoff_description="A personal assistant agent that can get the personal information of a user.",
            instructions=self._get_personal_instructions,
            mcp_servers=[self.mcp_server],
        )
        
        # 任务调度中心
        self.agents['triage'] = Agent[PersonalAssistantContext](
            name="Triage Agent",
            model=self.model,
            model_settings=self.model_settings,
            handoff_description="An Advanced Task Dispatch Center that precisely analyzes user intent, decomposes complex requests into executable sub-tasks, and coordinates the most appropriate agents to deliver comprehensive, integrated responses.",
            instructions=self._get_triage_instructions,
            handoffs=[
                self.agents['weather'],
                self.agents['news'],
                self.agents['recipe'],
                self.agents['personal'],
            ]
        )
        
        print("✅ 所有智能体创建完成")
    
    def _setup_agent_relationships(self):
        """设置智能体之间的关系"""
        # 为任务调度中心添加所有其他智能体的转接关系
        triage = self.agents['triage']
        for agent_name in ['weather', 'news', 'recipe', 'personal']:
            if agent_name != 'triage':
                triage.handoffs.append(self.agents[agent_name])
    
    def create_user_context(self, user_id: int) -> PersonalAssistantContext:
        """
        创建用户上下文
        
        Args:
            user_id: 用户ID
            
        Returns:
            PersonalAssistantContext: 用户上下文对象
        """
        try:
            print(f"👤 正在创建用户 {user_id} 的上下文...")
            
            # 初始化服务
            user_service = UserService()
            preference_service = PreferenceService(self.db_client)
            todo_service = TodoService(self.db_client)
            
            # 获取用户基本信息
            user_name = f"User {user_id}"
            lat = "Unknown"
            lng = "Unknown"
            
            user = user_service.get_user(user_id)
            if user:
                user_name = user.name
                lat = user.address.geo.lat
                lng = user.address.geo.lng
                print(f"✅ 获取用户信息: {user_name}")
            
            # 获取用户偏好
            user_preferences = {}
            try:
                prefs = preference_service.get_all_user_preferences(user_id)
                if prefs:
                    user_preferences = prefs
                    print(f"✅ 获取用户偏好: {len(user_preferences)} 个类别")
            except Exception as e:
                print(f"⚠️  获取用户偏好失败: {e}")
            
            # 获取待办事项
            todos = []
            try:
                user_todos = todo_service.get_user_todos(user_id, limit=50)
                if user_todos:
                    todos = user_todos
                    print(f"✅ 获取待办事项: {len(todos)} 个")
            except Exception as e:
                print(f"⚠️  获取待办事项失败: {e}")
            
            # 创建上下文
            context = PersonalAssistantContext(
                user_id=user_id,
                user_name=user_name,
                lat=lat,
                lng=lng,
                user_preferences=user_preferences,
                todos=todos
            )
            
            print(f"🎉 用户 {user_name} 的上下文创建完成")
            return context
            
        except Exception as e:
            print(f"❌ 创建用户上下文失败: {e}")
            # 返回默认上下文
            return PersonalAssistantContext(
                user_id=user_id,
                user_name=f"User {user_id}",
                lat="Unknown",
                lng="Unknown",
                user_preferences={},
                todos=[]
            )
    
    # 智能体指令生成方法
    def _get_weather_instructions(self, context: RunContextWrapper[PersonalAssistantContext], agent: Agent[PersonalAssistantContext]) -> str:
        """生成天气智能体指令"""
        ctx = context.context
        return (
            f"{RECOMMENDED_PROMPT_PREFIX} "
            "You are a weather agent. You can use your tools to get the weather of a location."
            f"The user's location is {ctx.lat}, {ctx.lng}."
        )
    
    def _get_news_instructions(self, context: RunContextWrapper[PersonalAssistantContext], agent: Agent[PersonalAssistantContext]) -> str:
        """生成新闻智能体指令"""
        ctx = context.context
        return (
            f"{RECOMMENDED_PROMPT_PREFIX} "
            "You are a news agent. You can use your tools to get the news of a location."
            f"The user's location is {ctx.lat}, {ctx.lng}."
            f"The user's preferences are {ctx.user_preferences}."
        )
    
    def _get_recipe_instructions(self, context: RunContextWrapper[PersonalAssistantContext], agent: Agent[PersonalAssistantContext]) -> str:
        """生成菜谱智能体指令"""
        ctx = context.context
        return (
            f"{RECOMMENDED_PROMPT_PREFIX} "
            "You are a recipe agent. You can use your tools to get the recipe of a location."
            "You input is must be english."
            f"The user's location is {ctx.lat}, {ctx.lng}."
            f"The user's preferences are {ctx.user_preferences}."
        )
    
    def _get_personal_instructions(self, context: RunContextWrapper[PersonalAssistantContext], agent: Agent[PersonalAssistantContext]) -> str:
        """生成个人助手智能体指令"""
        ctx = context.context
        return (
            f"{RECOMMENDED_PROMPT_PREFIX} "
            "You are a personal assistant agent. You can use your tools to get the personal information of a user."
            "You can manage the user's preferences, todos, and notes."
            f"The user's name is {ctx.user_name}."
            f"The user's id is {ctx.user_id}."
            f"The user's location is {ctx.lat}, {ctx.lng}."
            f"The user's preferences are {ctx.user_preferences}."
            f"The user's todos are {ctx.todos}."
        )
    
    def _get_triage_instructions(self, context: RunContextWrapper[PersonalAssistantContext], agent: Agent[PersonalAssistantContext]) -> str:
        """生成任务调度中心指令"""
        ctx = context.context
        return (
            f"{RECOMMENDED_PROMPT_PREFIX} "
            "You are an Advanced Task Dispatch Center. Your core mission is to precisely parse user intent, decompose complex requests into a series of specific, executable sub-tasks, and then call the most appropriate agents to efficiently complete these tasks. Finally, you need to integrate all agent execution results into a clear, coherent, and valuable final response for the user.\n\n"
            f"User Input: user_name: {ctx.user_name}, user_id: {ctx.user_id}"
            "Available Agents and Their Functions:\n"
            "1. Recipe Agent: Handles all food, recipe, restaurant, and culinary recommendation queries. Call when users mention keywords like 'what to eat', 'recipes', 'specialty foods', 'restaurants', etc.\n"
            "2. Weather Agent: Provides real-time weather forecasts for specified locations and times, future weather trends, and weather-based suggestions for clothing, travel, and umbrella needs. Call when users mention 'weather', 'will it rain', 'cold or not', 'what to wear', etc.\n"
            "3. News Agent: Queries global and local latest news, specific topic information (such as travel, technology, finance) and updates. Call when users need to understand recent situations about places or events, or need background information for planning.\n"
            "4. Personal Assistant: A multi-functional assistant managing user personal information with sub-modules for note management, to-do list management, and personal preference management. Call when tasks involve recording information, creating action items, or managing personal preferences.\n\n"
            "Your approach: Analyze intent → Decompose tasks → Call appropriate agents → Integrate results → Deliver comprehensive response.\n\n"
            "Important Principle: For clear and specific single-domain requests, directly handoff to the specialized agent without complex decomposition. Only use multi-agent coordination for complex, multi-domain tasks that require integration of different types of information.\n\n"
            "Example Workflow:\n"
            "User Input: '我明天要去法国巴黎玩，给我出一个规划。'\n"
            "Your Chain of Thought:\n"
            "1. Intent Analysis: User needs a travel plan for Paris tomorrow - this is a complex task requiring multiple types of information.\n"
            "2. Task Decomposition & Planning:\n"
            "   - Sub-task 1: Get Paris weather for tomorrow to provide clothing and travel suggestions → Call Weather Agent\n"
            "   - Sub-task 2: Query recent Paris news for any travel-affecting events or interesting activities → Call News Agent\n"
            "   - Sub-task 3: Recommend Paris specialty foods or cuisines → Call Recipe Agent\n"
            "   - Sub-task 4: Summarize all information into a complete plan and interact with user to confirm if recording is needed → Call Personal Assistant (notes/todo/preferences)\n"
            "3. Execute agents in logical order, then integrate all results into a comprehensive Paris travel plan."
        )
    
    # 钩子函数
    async def refresh_user_preferences(self, context: RunContextWrapper[PersonalAssistantContext]) -> None:
        """刷新用户偏好信息"""
        preference_service = PreferenceService(self.db_client)
        context.context.user_preferences = preference_service.get_all_user_preferences(context.context.user_id)
    
    async def refresh_user_todos(self, context: RunContextWrapper[PersonalAssistantContext]) -> None:
        """刷新用户待办事项"""
        todo_service = TodoService(self.db_client)
        context.context.todos = todo_service.get_user_todos(context.context.user_id, limit=50)
    
    # 公共接口方法
    def get_agent(self, agent_name: str) -> Agent[PersonalAssistantContext]:
        """
        获取指定的智能体
        
        Args:
            agent_name: 智能体名称 ('weather', 'news', 'recipe', 'personal', 'triage')
            
        Returns:
            Agent: 智能体对象
            
        Raises:
            RuntimeError: 如果管理器未初始化
            KeyError: 如果智能体不存在
        """
        if not self._initialized:
            raise RuntimeError("PersonalAssistantManager 尚未初始化，请先调用 initialize()")
        
        if agent_name not in self.agents:
            raise KeyError(f"智能体 '{agent_name}' 不存在。可用的智能体: {list(self.agents.keys())}")
        
        return self.agents[agent_name]
    
    def get_triage_agent(self) -> Agent[PersonalAssistantContext]:
        """获取任务调度中心智能体"""
        return self.get_agent('triage')
    
    def get_weather_agent(self) -> Agent[PersonalAssistantContext]:
        """获取天气智能体"""
        return self.get_agent('weather')
    
    def get_news_agent(self) -> Agent[PersonalAssistantContext]:
        """获取新闻智能体"""
        return self.get_agent('news')
    
    def get_recipe_agent(self) -> Agent[PersonalAssistantContext]:
        """获取菜谱智能体"""
        return self.get_agent('recipe')
    
    def get_personal_agent(self) -> Agent[PersonalAssistantContext]:
        """获取个人助手智能体"""
        return self.get_agent('personal')
    
    @property
    def is_initialized(self) -> bool:
        """检查管理器是否已初始化"""
        return self._initialized
    
    @property
    def available_agents(self) -> List[str]:
        """获取可用智能体列表"""
        return list(self.agents.keys())
    
    def __str__(self) -> str:
        """字符串表示"""
        status = "已初始化" if self._initialized else "未初始化"
        return f"PersonalAssistantManager(状态: {status}, 智能体数量: {len(self.agents)})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return f"PersonalAssistantManager(initialized={self._initialized}, agents={list(self.agents.keys())})" 