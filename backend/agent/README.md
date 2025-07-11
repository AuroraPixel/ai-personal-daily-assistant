# AI驱动的个人日常助手系统

这是一个基于多智能体架构的个人日常助手系统，采用Hub-and-Spoke（中心辐射）设计模式。

## 系统架构

### 核心组件

- **协调代理 (Coordination Agent)**: 系统的中心枢纽，负责智能路由和请求分配
- **天气代理 (Weather Agent)**: 专门处理天气查询和预报服务
- **菜谱代理 (Recipe Agent)**: 专门处理菜谱搜索和烹饪建议
- **新闻代理 (News Agent)**: 专门处理新闻获取和信息咨询
- **个人助理代理 (Personal Assistant Agent)**: 专门处理任务管理和个人事务

### 系统特性

- ✅ **智能路由**: 自动识别用户意图并转接给合适的专业代理
- ✅ **上下文共享**: 所有代理共享用户上下文信息
- ✅ **安全防护**: 多层护栏系统确保输入安全和相关性
- ✅ **MCP集成**: 通过MCP协议统一外部工具调用
- ✅ **无缝转接**: 代理间平滑切换，用户体验流畅
- ✅ **个性化服务**: 基于用户偏好提供定制化建议

## 快速开始

### 环境准备

1. 确保已安装所需依赖:
```bash
pip install -r requirements.txt
```

2. 设置环境变量:
```bash
export OPENAI_API_KEY="your_openai_api_key"
export OPENAI_API_BASE_URL="your_openai_base_url"
```

3. 启动MCP服务器 (在8002端口):
```bash
cd backend/mcp-serve
python mcp_server.py
```

### 基本使用

```python
from backend.agent.personal_assistant import (
    coordination_agent,
    create_initial_context,
    initialize_mcp_servers,
    cleanup_mcp_servers
)
from agents import Runner

async def main():
    # 1. 初始化MCP服务器
    await initialize_mcp_servers()
    
    # 2. 创建用户上下文
    context = create_initial_context()
    
    # 3. 开始对话
    result = await Runner.run(
        coordination_agent, 
        "你好，我想查询北京的天气", 
        context=context
    )
    
    print(result.final_output)
    
    # 4. 清理资源
    await cleanup_mcp_servers()

# 运行示例
import asyncio
asyncio.run(main())
```

## 使用场景示例

### 天气查询
```python
# 用户输入: "今天北京的天气怎么样？"
# 系统会自动转接给天气代理处理
```

### 菜谱搜索
```python
# 用户输入: "推荐一道简单的中式菜谱"
# 系统会自动转接给菜谱代理处理
```

### 新闻获取
```python
# 用户输入: "有什么科技新闻吗？"
# 系统会自动转接给新闻代理处理
```

### 任务管理
```python
# 用户输入: "帮我添加一个提醒，明天下午3点开会"
# 系统会自动转接给个人助理代理处理
```

## 代理功能详解

### 协调代理 (coordination_agent)
- 🎯 **智能路由**: 分析用户意图，选择合适的专业代理
- 🔄 **回流处理**: 接收其他代理完成任务后的回流
- 💬 **直接对话**: 处理简单问候和确认类对话

### 天气代理 (weather_agent)
- 🌤️ **天气查询**: 获取指定位置的实时天气信息
- 📈 **预报服务**: 提供未来几天的天气预报
- 💡 **生活建议**: 根据天气情况提供出行和穿衣建议
- 🗺️ **天气地图**: 显示交互式天气地图界面

### 菜谱代理 (recipe_agent)
- 🔍 **菜谱搜索**: 根据关键词和偏好搜索菜谱
- 👨‍🍳 **烹饪指导**: 提供详细制作步骤和技巧
- 🥗 **营养建议**: 提供营养搭配和健康建议
- 📱 **详情显示**: 显示图文并茂的菜谱详情界面

### 新闻代理 (news_agent)
- 📰 **新闻获取**: 获取最新的新闻资讯
- 🎯 **主题筛选**: 根据用户兴趣筛选相关新闻
- 📊 **摘要分析**: 提供新闻摘要和背景分析
- 🔔 **个性推荐**: 基于用户偏好推荐相关内容

### 个人助理代理 (personal_assistant_agent)
- ✅ **待办管理**: 添加、查看、修改待办事项
- ⏰ **提醒设置**: 创建时间提醒和重要事件提醒
- 📝 **笔记保存**: 保存个人笔记，支持标签分类
- ⚙️ **偏好设置**: 管理用户个人偏好和设置
- 📊 **状态查看**: 查看用户信息和任务统计

## 系统配置

### MCP服务器配置
系统通过MCP协议连接外部工具服务:
- **服务地址**: http://127.0.0.1:8002/mcp
- **服务名称**: personal_assistant_tools
- **支持工具**: 天气查询、菜谱搜索、新闻获取

### 护栏系统
- **相关性检查**: 确保用户输入与个人助手服务相关
- **安全检测**: 防范恶意攻击和系统绕过尝试
- **优雅处理**: 护栏触发时提供友好提示

### 上下文管理
用户上下文包含以下信息:
- 用户基础信息 (ID、姓名、偏好)
- 会话状态 (位置、会话ID、对话历史)
- 任务数据 (待办、提醒、笔记)
- 服务状态 (天气历史、菜谱偏好、新闻兴趣)

## 扩展开发

### 添加新的专业代理

1. 创建代理类:
```python
new_agent = Agent[PersonalAssistantContext](
    name="New Agent",
    model=model,
    instructions="代理指令",
    tools=[your_tools],
    input_guardrails=[relevance_guardrail, safety_guardrail],
)
```

2. 添加到协调代理的转接列表:
```python
coordination_agent.handoffs.append(
    handoff(agent=new_agent, on_handoff=your_handoff_function)
)
```

3. 配置回流关系:
```python
new_agent.handoffs.append(coordination_agent)
```

### 添加新的工具函数
```python
@function_tool(
    name_override="your_tool_name",
    description_override="工具描述"
)
async def your_tool_function(
    context: RunContextWrapper[PersonalAssistantContext],
    param1: str,
    param2: str = "default"
) -> str:
    """工具功能实现"""
    # 工具逻辑
    return "结果"
```

## 注意事项

1. **MCP服务器依赖**: 确保MCP服务器在8002端口正常运行
2. **环境变量**: 正确设置OpenAI API相关环境变量
3. **资源管理**: 使用完毕后调用cleanup_mcp_servers()清理资源
4. **错误处理**: 系统内置优雅降级机制，MCP服务不可用时仍可提供基础功能
5. **中文支持**: 所有提示词和交互都支持中文，便于本地化使用

## 故障排除

### MCP连接失败
- 检查MCP服务器是否在8002端口运行
- 确认网络连接和防火墙设置
- 查看MCP服务器日志获取详细错误信息

### API调用失败
- 验证OpenAI API密钥是否正确
- 检查API基础URL设置
- 确认网络可以访问OpenAI服务

### 代理转接异常
- 检查护栏系统是否正常工作
- 验证代理间handoff关系配置
- 查看上下文信息是否完整

---

这个系统展示了如何使用现代AI技术构建智能、模块化、可扩展的个人助手服务。通过明确的职责分工和灵活的转接机制，为用户提供专业、高效的多领域服务支持。 