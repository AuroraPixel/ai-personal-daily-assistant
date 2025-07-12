from __future__ import annotations as _annotations

import random
import string
import uuid
from datetime import datetime
from agents.model_settings import ModelSettings
from pydantic import BaseModel
from agents.extensions.models.litellm_model import LitellmModel
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.mcp import ToolFilterContext
from dotenv import load_dotenv
import os

load_dotenv()

from agents import (
    Agent,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    function_tool,
    handoff,
    GuardrailFunctionOutput,
    input_guardrail,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# =========================
# 系统配置与初始化模块
# =========================

# =========================
# 类型：模型配置-大语言模型设置
# 功能描述：配置系统使用的大语言模型参数和连接设置
# 模型信息：
#   - 模型名称：gpt-4o（OpenAI的GPT-4优化版本）
#   - 基础URL：从环境变量OPENAI_API_BASE_URL获取
#   - API密钥：从环境变量OPENAI_API_KEY获取
# 技术实现：使用LitellmModel包装器支持多种LLM提供商
# 配置来源：使用dotenv加载环境变量确保安全性
# 应用范围：所有智能代理和护栏都使用此模型配置
# =========================
model = LitellmModel(
    model="gpt-4o",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

# =========================
# 类型：模型配置
# =========================
model_setting = ModelSettings(
    temperature=0.6, # 控制创造性
    top_p=0.9, # 词汇的多样性
    tool_choice="auto", # 自动选择工具
    parallel_tool_calls=True, # 并行调用工具
    truncation="auto", # 截断策略
)

# =========================
# 类型：mcp工具动态策略过滤器
# 功能描述：根据agent的名称，动态过滤出对应的mcp工具
# 输入内容：
#   - context: 工具过滤上下文
#   - tool: 工具名称
# =========================
def tools_prefix_filter(context: ToolFilterContext, tool) -> bool:
    agent_name = context.agent.name
    if agent_name == "Weather Agent":
        return tool.name.startswith("weather_")
    elif agent_name == "News Agent":
        return tool.name.startswith("news_")
    elif agent_name == "Recipe Agent":
        return tool.name.startswith("recipe_")
    elif agent_name == "Personal Assistant Agent":
        return tool.name.startswith("data_")
    return False


# =========================
# 类型：MCP服务配置-模型上下文协议
# 功能描述：配置MCP（Model Context Protocol）服务器用于扩展工具调用能力
# 服务信息：
#   - 服务名称：personal_assistant_tools（个人助手工具集合）
#   - 服务地址：http://127.0.0.1:8002/mcp（本地MCP服务器）
# 技术作用：
#   1. 提供额外的工具调用能力（天气查询、菜谱搜索、新闻获取）
#   2. 通过HTTP流式协议与MCP服务器通信
#   3. 扩展代理的外部数据访问能力
# 集成方式：作为外部工具服务集成到代理系统中
# 注意事项：需要确保MCP服务器在指定端口运行
# =========================
personal_assistant_mcp_server = MCPServerStreamableHttp(
    name="personal_assistant_tools", # 个人助手工具调用
    params={
        "url": "http://127.0.0.1:8002/mcp",
    },
    tool_filter=tools_prefix_filter
)




# =========================
# 类型：智能体-相关性判断
# 功能描述：判断用户消息是否与个人日常助手服务相关
# 提示词内容：（"判断用户消息是否与个人日常助手服务相关，包括："
#            "- 天气查询、预报咨询"
#            "- 菜谱搜索、烹饪建议" 
#            "- 新闻获取、信息咨询"
#            "- 个人任务管理（待办事项、提醒、笔记）"
#            "- 正常对话交流（问候、确认等）"
#            "如果相关则返回 is_relevant=True，否则返回 False，并附上简要理由。"
#            "重要：只评估最新用户消息，不评估对话历史。"）
# 输入内容：用户消息
# 输出内容：是否相关，以及相关性判断的依据
# =========================
relevance_guardrail_agent = Agent(
    model=model,
    model_settings=model_setting,
    name="Personal Assistant Relevance Guardrail",
    instructions=(
        "判断用户消息是否与个人日常助手服务相关，包括："
        "- 天气查询、预报咨询"
        "- 菜谱搜索、烹饪建议" 
        "- 新闻获取、信息咨询"
        "- 个人任务管理（待办事项、提醒、笔记）"
        "- 生活咨询和建议"
        "- 正常对话交流（问候、确认等）"
        "如果相关则返回 is_relevant=True，否则返回 False，并附上简要理由。"
        "重要：只评估最新用户消息，不评估对话历史。"
        "客户发送类似'你好'、'好的'或任何其他具有对话性质的消息都是可以的，"
        "但如果回复不是对话性的，那它必须与个人助手服务有一定关联。"
    ),
)


weather_agent = Agent(
    name="Weather Agent",
    model=model,
    model_settings=model_setting,
    handoff_description="专业的天气信息查询和预报代理",
    instructions="你是一个专业的天气信息查询和预报代理，请根据用户输入的天气信息，给出相应的天气预报和建议。",
    mcp_servers=[personal_assistant_mcp_server],
)

# =========================
# 类型：业务代理-菜谱搜索服务
# 功能描述：专门处理用户菜谱搜索和烹饪建议请求的智能代理
# 服务范围：
#   - 菜谱搜索和推荐
#   - 烹饪指导和技巧分享
#   - 营养搭配建议
#   - 菜谱详情界面显示
# 可用工具：
#   - display_recipe_detail: 显示菜谱详细信息
# MCP服务器：
#   - personal_assistant_mcp_server: 用于菜谱搜索功能
# 转接描述：专业的菜谱搜索和烹饪建议代理
# 安全防护：
#   - relevance_guardrail: 确保输入与服务相关
#   - safety_guardrail: 防范恶意攻击尝试
# 交互模式：从协调代理接收转接，完成后可转回协调代理
# 上下文需求：需要用户饮食偏好信息
# =========================
recipe_agent = Agent(
    name="Recipe Agent",
    model=model,
    model_settings=model_setting,
    handoff_description="专业的菜谱搜索和烹饪建议代理",
    instructions="你是一个专业的菜谱搜索和烹饪建议代理，请根据用户输入的菜谱信息，给出相应的菜谱和烹饪建议。",
    mcp_servers=[personal_assistant_mcp_server],
)

# =========================
# 类型：业务代理-新闻获取服务
# 功能描述：专门处理用户新闻获取和信息咨询请求的智能代理
# 服务范围：
#   - 最新新闻获取
#   - 特定主题新闻搜索
#   - 新闻摘要和分析
#   - 个性化新闻推荐
# MCP服务器：
#   - personal_assistant_mcp_server: 用于新闻查询功能
# 转接描述：专业的新闻获取和信息咨询代理
# 安全防护：
#   - relevance_guardrail: 确保输入与服务相关
#   - safety_guardrail: 防范恶意攻击尝试
# 交互模式：从协调代理接收转接，完成后可转回协调代理
# 上下文需求：需要用户新闻兴趣信息
# =========================
news_agent = Agent(
    name="News Agent",
    model=model,
    model_settings=model_setting,
    handoff_description="专业的新闻获取和信息咨询代理",
    instructions="你是一个专业的新闻获取和信息咨询代理，请根据用户输入的新闻信息，给出相应的新闻和信息咨询。",
    mcp_servers=[personal_assistant_mcp_server],
)
# =========================
# 类型：核心代理-协调调度中心
# 功能描述：系统的核心路由代理，负责接收所有用户请求并分配给合适的专门代理
# 核心职责：
#   - 接收和分析用户请求
#   - 判断请求类型和复杂度
#   - 将请求路由到最合适的专门代理
#   - 作为各专门代理的回流中心
# 转接描述：智能协调代理，负责分析用户需求并分配给合适的专业代理
# 转接目标：
#   - weather_agent: 天气查询（带钩子函数）
#   - recipe_agent: 菜谱搜索（带钩子函数）
#   - news_agent: 新闻获取（带钩子函数）
#   - personal_assistant_agent: 个人任务管理（带钩子函数）
# 工作模式：
#   1. 作为系统入口接收所有用户请求
#   2. 基于请求内容智能分析和分类
#   3. 选择最合适的专门代理进行转接
#   4. 接收其他代理完成任务后的回流
# 智能路由原则：
#   - 天气相关 -> 天气代理
#   - 菜谱、烹饪相关 -> 菜谱代理
#   - 新闻、资讯相关 -> 新闻代理
#   - 任务管理、个人助理相关 -> 个人助理代理
#   - 复杂或综合请求 -> 保持在协调代理处理
# 安全防护：
#   - relevance_guardrail: 确保输入与服务相关
#   - safety_guardrail: 防范恶意攻击尝试
# 系统地位：协调代理是整个个人助手系统的中枢神经
# =========================
coordination_agent = Agent(
    name="Coordination Agent",
    model=model,
    model_settings=model_setting,
    handoff_description="智能协调代理，负责分析用户需求并分配给合适的专业代理",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX} "
        "您是智能协调代理，是整个个人日常助手系统的中心枢纽。您的主要职责是理解用户需求并将请求转交给最合适的专业代理。\n\n"
        "可用的专业代理服务：\n"
        "- 天气代理：处理天气查询、预报咨询、气候相关问题\n"
        "- 菜谱代理：处理菜谱搜索、烹饪建议、营养搭配问题\n"
        "- 新闻代理：处理新闻获取、资讯查询、时事分析问题\n"
        "工作原则：\n"
        "1. 仔细分析用户的请求内容和意图\n"
        "2. 根据请求类型选择最合适的专业代理进行转接\n"
        "3. 对于简单的问候、确认等对话，可以直接回复\n"
        "4. 对于复杂的综合性请求，可以提供概览并建议用户选择具体服务\n"
        "5. 如果用户输入的天气信息是文字描述，请你自我转为经纬度坐标，然后再调用工具查询信息。\n"
        "6. 如果用户输入内容可能涉及天气,菜谱,新闻相关,可以先调用相关代理执行任务，然后根据代理返回结果，给出综合答案。"
        "7. 始终保持友好、专业的服务态度\n\n"
        "您可以使用工具将问题委托给其他合适的代理。当专业代理完成任务后，用户会回到您这里继续对话。"
    ),
    tools=[
        weather_agent.as_tool(
            tool_name="weather_agent",
            tool_description="获取天气相关信息",
        ),
        recipe_agent.as_tool(
            tool_name="recipe_agent",
            tool_description="获取菜谱相关信息",
        ),
        news_agent.as_tool(
            tool_name="news_agent",
            tool_description="获取新闻相关信息",
        ),
    ],
) 

# =========================
# MCP服务器连接管理模块
# =========================

# =========================
# 类型：连接管理函数-MCP服务器初始化
# 功能描述：初始化并连接MCP服务器，确保服务器在使用前已建立连接
# 业务逻辑：
#   1. 尝试连接到指定的MCP服务器
#   2. 验证连接是否成功建立
#   3. 记录连接状态以便后续管理
#   4. 处理连接失败的异常情况
# 连接目标：个人助手工具服务器
# 服务地址：http://127.0.0.1:8002/mcp
# 执行时机：应用启动时调用
# 错误处理：记录连接失败信息，但不中断应用启动
# =========================
async def initialize_mcp_servers():
    """初始化并连接所有MCP服务器"""
    try:
        print("正在连接个人助手MCP服务器...")
        await personal_assistant_mcp_server.connect()
        print(f"✅ MCP服务器连接成功: {personal_assistant_mcp_server.name}")
        return True
    except Exception as e:
        print(f"❌ MCP服务器连接失败: {personal_assistant_mcp_server.name}")
        print(f"错误详情: {e}")
        print("请确保MCP服务器在 http://127.0.0.1:8002/mcp 运行")
        return False

# =========================
# 类型：连接管理函数-MCP服务器清理
# 功能描述：断开MCP服务器连接，清理资源
# 业务逻辑：
#   1. 安全断开所有MCP服务器连接
#   2. 释放相关网络资源
#   3. 记录断开连接状态
#   4. 处理断开过程中的异常
# 执行时机：应用关闭时调用
# 错误处理：忽略断开过程中的错误，确保应用能正常关闭
# =========================
async def cleanup_mcp_servers():
    """清理并断开所有MCP服务器连接"""
    try:
        print("正在断开个人助手MCP服务器连接...")
        await personal_assistant_mcp_server.cleanup()
        print(f"✅ MCP服务器断开成功: {personal_assistant_mcp_server.name}")
    except Exception as e:
        print(f"⚠️ MCP服务器断开时出现错误: {e}")

# =========================
# 系统入口点和使用示例
# =========================

# =========================
# 类型：使用示例和文档
# 功能描述：展示如何使用个人日常助手系统的示例代码
# 使用方式：
#   1. 首先调用 initialize_mcp_servers() 初始化服务
#   2. 创建初始上下文 create_initial_context()
#   3. 使用 coordination_agent 作为主要入口点
#   4. 应用结束时调用 cleanup_mcp_servers() 清理资源
# 
# 示例代码：
# ```python
# # 系统初始化
# await initialize_mcp_servers()
# context = create_initial_context()
# 
# # 开始对话
# from agents import Runner
# result = await Runner.run(
#     coordination_agent, 
#     "你好，我想查询北京的天气", 
#     context=context
# )
# 
# # 系统清理
# await cleanup_mcp_servers()
# ```
# 
# 主要代理说明：
#   - coordination_agent: 系统主入口，负责智能路由
#   - weather_agent: 天气查询专业代理
#   - recipe_agent: 菜谱搜索专业代理
#   - news_agent: 新闻获取专业代理
#   - personal_assistant_agent: 个人任务管理专业代理
# 
# 注意事项：
#   - 确保MCP服务器在正确端口运行
#   - 环境变量OPENAI_API_KEY和OPENAI_API_BASE_URL需正确设置
#   - 系统设计遵循Hub-and-Spoke模式，协调代理为中心
# =========================

# 导出主要组件供外部使用
__all__ = [
    # 上下文和初始化
    'PersonalAssistantContext',
    'create_initial_context',
    
    # 主要代理
    'coordination_agent',
    'weather_agent', 
    'recipe_agent',
    'news_agent',
    'personal_assistant_agent',
    
    # MCP服务器管理
    'initialize_mcp_servers',
    'cleanup_mcp_servers',
    
    # 工具函数
    'add_reminder_tool',
    'save_note_tool',
    'add_todo_tool',
    'update_preference_tool',
    'display_todo_list',
    'display_weather_map',
    'display_recipe_detail',
    'view_user_info'
] 