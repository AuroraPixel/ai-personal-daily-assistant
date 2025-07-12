# 个人助手管理器 (PersonalAssistantManager)

这是一个重构版本的个人助手系统，将所有功能封装到一个管理器类中，便于使用和维护。

## 🌟 主要特性

- **🏗️ 面向对象设计**: 所有功能封装在`PersonalAssistantManager`类中
- **🔌 外部依赖注入**: 数据库客户端从外部传入，提高灵活性
- **🤖 多智能体管理**: 统一管理5个专门的智能体
- **⚙️ 异步初始化**: 支持异步初始化所有服务
- **🛡️ 错误处理**: 完善的异常处理和错误提示
- **📝 类型支持**: 完整的类型注解和IDE支持

## 🚀 快速开始

### 1. 基本使用

```python
import asyncio
from core.database_core import DatabaseClient
from agent.personal_assistant_manager import PersonalAssistantManager
from agents import Runner

async def main():
    # 1. 初始化数据库客户端
    db_client = DatabaseClient()
    db_client.initialize()
    db_client.create_tables()
    
    # 2. 创建个人助手管理器
    manager = PersonalAssistantManager(db_client)
    
    # 3. 初始化管理器
    await manager.initialize()
    
    # 4. 创建用户上下文
    context = manager.create_user_context(user_id=1)
    
    # 5. 获取任务调度中心智能体
    agent = manager.get_triage_agent()
    
    # 6. 使用智能体处理用户请求
    response = await Runner.run(agent, "你好", context=context)
    print(f"助手回复: {response.final_output}")

# 运行示例
asyncio.run(main())
```

### 2. 详细示例

```python
import asyncio
from core.database_core import DatabaseClient
from agent.personal_assistant_manager import PersonalAssistantManager
from agents import Runner

async def detailed_example():
    # 数据库初始化
    db_client = DatabaseClient()
    db_client.initialize()
    db_client.create_tables()
    
    # 创建管理器（可以自定义MCP服务器地址）
    manager = PersonalAssistantManager(
        db_client=db_client,
        mcp_server_url="http://127.0.0.1:8002/mcp"
    )
    
    # 初始化管理器
    success = await manager.initialize()
    if not success:
        print("初始化失败")
        return
    
    # 创建用户上下文
    context = manager.create_user_context(user_id=1)
    print(f"用户上下文: {context.user_name}")
    
    # 查看可用的智能体
    print(f"可用智能体: {manager.available_agents}")
    
    # 使用不同的智能体
    agents = {
        "任务调度": manager.get_triage_agent(),
        "天气查询": manager.get_weather_agent(),
        "新闻资讯": manager.get_news_agent(),
        "菜谱推荐": manager.get_recipe_agent(),
        "个人助手": manager.get_personal_agent(),
    }
    
    for name, agent in agents.items():
        print(f"✅ {name}: {agent.name}")
    
    # 使用任务调度中心处理复杂请求
    triage_agent = manager.get_triage_agent()
    test_requests = [
        "你好，请介绍一下你的功能",
        "今天天气怎么样？",
        "有什么新闻吗？",
        "推荐一个菜谱",
        "帮我记录一个待办事项"
    ]
    
    for request in test_requests:
        try:
            response = await Runner.run(triage_agent, request, context=context)
            print(f"用户: {request}")
            print(f"助手: {response.final_output[:100]}...")
            print("-" * 50)
        except Exception as e:
            print(f"处理失败: {e}")

asyncio.run(detailed_example())
```

## 🏗️ 架构设计

### 类结构

```
PersonalAssistantManager
├── __init__(db_client, mcp_server_url)
├── initialize() -> bool
├── create_user_context(user_id) -> PersonalAssistantContext
├── get_agent(agent_name) -> Agent
├── get_triage_agent() -> Agent
├── get_weather_agent() -> Agent
├── get_news_agent() -> Agent
├── get_recipe_agent() -> Agent
├── get_personal_agent() -> Agent
├── refresh_user_preferences(context)
├── refresh_user_todos(context)
└── Properties:
    ├── is_initialized -> bool
    └── available_agents -> List[str]
```

### 智能体类型

1. **🎯 Triage Agent (任务调度中心)**
   - 智能分析用户意图
   - 路由到合适的专门智能体
   - 整合多个智能体的结果

2. **🌤️ Weather Agent (天气智能体)**
   - 实时天气查询
   - 天气预报
   - 出行建议

3. **📰 News Agent (新闻智能体)**
   - 最新新闻获取
   - 个性化新闻推荐
   - 特定主题新闻

4. **🍳 Recipe Agent (菜谱智能体)**
   - 菜谱搜索
   - 烹饪建议
   - 营养搭配

5. **📝 Personal Agent (个人助手)**
   - 待办事项管理
   - 笔记记录
   - 个人偏好设置

## 🔧 配置说明

### 环境变量

```bash
# OpenAI API 配置
CUSTOMIZE_OPENAI_API_BASE_URL=https://api.openai.com/v1
CUSTOMIZE_OPENAI_API_KEY=your_api_key_here

# 数据库配置（根据你的数据库配置设置）
# 详见 core/database_core/config.py
```

### MCP服务器

确保MCP服务器在指定端口运行：

```bash
# 启动MCP服务器
cd backend/mcp-serve
python mcp_server.py
```

默认地址：`http://127.0.0.1:8002/mcp`

## 🎯 使用场景

### 1. 天气查询

```python
agent = manager.get_weather_agent()
response = await Runner.run(agent, "今天北京天气怎么样？", context=context)
```

### 2. 新闻获取

```python
agent = manager.get_news_agent()
response = await Runner.run(agent, "有什么科技新闻吗？", context=context)
```

### 3. 菜谱推荐

```python
agent = manager.get_recipe_agent()
response = await Runner.run(agent, "推荐一道简单的中式菜谱", context=context)
```

### 4. 个人任务管理

```python
agent = manager.get_personal_agent()
response = await Runner.run(agent, "帮我添加一个提醒：明天下午3点开会", context=context)
```

### 5. 复杂任务处理

```python
agent = manager.get_triage_agent()
response = await Runner.run(agent, "我明天要去巴黎，给我做个出行规划", context=context)
```

## 🔍 API 参考

### PersonalAssistantManager

#### 构造函数
```python
def __init__(self, db_client: DatabaseClient, mcp_server_url: str = "http://127.0.0.1:8002/mcp")
```

#### 方法

##### `async initialize() -> bool`
初始化管理器和所有服务。

##### `create_user_context(user_id: int) -> PersonalAssistantContext`
创建用户上下文，包含用户信息、偏好和待办事项。

##### `get_agent(agent_name: str) -> Agent`
获取指定的智能体。

可用的智能体名称：
- `"triage"` - 任务调度中心
- `"weather"` - 天气智能体
- `"news"` - 新闻智能体
- `"recipe"` - 菜谱智能体
- `"personal"` - 个人助手

##### `get_triage_agent() -> Agent`
获取任务调度中心智能体。

##### `get_weather_agent() -> Agent`
获取天气智能体。

##### `get_news_agent() -> Agent`
获取新闻智能体。

##### `get_recipe_agent() -> Agent`
获取菜谱智能体。

##### `get_personal_agent() -> Agent`
获取个人助手智能体。

#### 属性

##### `is_initialized -> bool`
检查管理器是否已初始化。

##### `available_agents -> List[str]`
获取可用智能体列表。

### PersonalAssistantContext

```python
class PersonalAssistantContext(BaseModel):
    user_id: int                                    # 用户ID
    user_name: str                                  # 用户姓名
    lat: str                                        # 纬度
    lng: str                                        # 经度
    user_preferences: Dict[str, Dict[str, Any]]     # 用户偏好
    todos: List[Todo]                               # 待办事项
```

## 🐛 故障排除

### 常见问题

1. **MCP服务器连接失败**
   ```
   ❌ MCP服务器连接失败
   ```
   - 检查MCP服务器是否在运行
   - 确认端口号是否正确
   - 检查防火墙设置

2. **数据库连接失败**
   - 检查数据库服务是否运行
   - 确认数据库配置是否正确
   - 检查数据库权限

3. **智能体初始化失败**
   ```
   RuntimeError: PersonalAssistantManager 尚未初始化
   ```
   - 确保调用了 `await manager.initialize()`
   - 检查初始化返回值是否为True

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查管理器状态**
   ```python
   print(f"管理器状态: {manager}")
   print(f"可用智能体: {manager.available_agents}")
   print(f"是否已初始化: {manager.is_initialized}")
   ```

3. **逐步初始化**
   ```python
   # 分步骤初始化以定位问题
   await manager._initialize_mcp_server()
   manager._initialize_vector_database()
   manager._initialize_agents()
   ```

## 📚 更多示例

完整的使用示例请参考：
- `backend/agent/example_usage.py` - 详细的使用示例
- `backend/agent/personal_assistant_manager.py` - 源代码和文档

## 🤝 贡献

欢迎提交Issues和Pull Requests来改进这个项目。

## 📄 许可证

本项目使用MIT许可证。 