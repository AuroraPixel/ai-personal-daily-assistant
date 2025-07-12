# Service 业务层

这是AI个人日常助手的业务层，提供用户管理、偏好设置、笔记管理、待办事项等核心业务功能。

## 📁 目录结构

```
backend/service/
├── __init__.py              # 包初始化
├── models/                  # 数据模型层
│   ├── __init__.py
│   ├── user_preference.py   # 用户偏好设置模型
│   ├── note.py             # 笔记模型
│   └── todo.py             # 待办事项模型
├── services/               # 业务服务层
│   ├── __init__.py
│   ├── user_service.py     # 用户服务
│   ├── preference_service.py # 偏好设置服务
│   ├── note_service.py     # 笔记服务
│   └── todo_service.py     # 待办事项服务
├── example_usage.py        # 使用示例
└── README.md              # 文档
```

## 🎯 设计原则

### 分层架构
- **用户数据**: 来自JSONPlaceholder API，不存储在数据库
- **偏好设置**: 存储在MySQL数据库，JSON格式
- **笔记**: 存储在MySQL数据库，支持标签和状态
- **待办事项**: 存储在MySQL数据库，可关联笔记

### 数据分离
- 用户基础信息通过API获取
- 个人数据（偏好、笔记、待办）存储在数据库
- 保持数据的独立性和可扩展性

## 📊 数据模型

### UserPreference - 用户偏好设置
```python
class UserPreference(BaseModel):
    user_id: int          # 用户ID（来自JSONPlaceholder）
    preferences: str      # 偏好设置内容（JSON字符串）
    category: str         # 偏好设置类别
    last_updated: datetime # 最后更新时间
```

### Note - 笔记
```python
class Note(BaseModel):
    user_id: int          # 用户ID
    title: str           # 笔记标题
    content: str         # 笔记内容
    tags: str            # 笔记标签（逗号分隔）
    status: str          # 笔记状态（draft/published/archived）
    last_updated: datetime # 最后更新时间
```

### Todo - 待办事项
```python
class Todo(BaseModel):
    user_id: int          # 用户ID
    title: str           # 待办事项标题
    description: str     # 描述
    completed: bool      # 是否完成
    priority: str        # 优先级（high/medium/low）
    note_id: int         # 关联的笔记ID（可选）
    due_date: datetime   # 截止日期
    completed_at: datetime # 完成时间
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 确保MySQL服务运行
# 配置环境变量(.env文件)
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=your_password
DB_DATABASE=personal_assistant
```

### 2. 基础使用

#### 用户服务
```python
from service.services.user_service import UserService

user_service = UserService()

# 获取用户信息
user = user_service.get_user(1)
print(f"用户: {user.name} ({user.email})")

# 验证用户是否存在
exists = user_service.validate_user_exists(1)
print(f"用户存在: {exists}")
```

#### 偏好设置服务
```python
from service.services.preference_service import PreferenceService

preference_service = PreferenceService()

# 保存用户偏好
preferences = {
    "theme": "dark",
    "language": "zh-CN",
    "notifications": {"email": True, "push": False}
}
success = preference_service.save_user_preferences(1, preferences)

# 获取用户偏好
saved_preferences = preference_service.get_user_preferences(1)
print(f"偏好设置: {saved_preferences}")
```

#### 笔记服务
```python
from service.services.note_service import NoteService

note_service = NoteService()

# 创建笔记
note = note_service.create_note(
    user_id=1,
    title="我的笔记",
    content="笔记内容",
    tags=["工作", "重要"],
    status="draft"
)

# 搜索笔记
results = note_service.search_notes(1, "工作")
print(f"搜索到 {len(results)} 个笔记")
```

#### 待办事项服务
```python
from service.services.todo_service import TodoService
from datetime import datetime, timedelta

todo_service = TodoService()

# 创建待办事项
todo = todo_service.create_todo(
    user_id=1,
    title="完成项目",
    description="完成项目的开发工作",
    priority="high",
    due_date=datetime.now() + timedelta(days=7)
)

# 完成待办事项
success = todo_service.complete_todo(todo.id)
print(f"任务完成: {success}")
```

## 🔧 高级功能

### 关联笔记和待办事项
```python
# 创建笔记
note = note_service.create_note(
    user_id=1,
    title="项目计划",
    content="详细的项目计划和时间表"
)

# 创建关联的待办事项
todo = todo_service.create_todo(
    user_id=1,
    title="执行项目计划",
    description="按照计划执行项目",
    note_id=note.id  # 关联笔记
)

# 获取笔记相关的待办事项
related_todos = todo_service.get_todos_by_note(note.id)
```

### 数据统计
```python
# 笔记统计
note_stats = note_service.get_notes_statistics(1)
print(f"笔记统计: {note_stats}")

# 待办事项统计
todo_stats = todo_service.get_todos_statistics(1)
print(f"待办事项统计: {todo_stats}")
```

### 偏好设置分类
```python
# 保存不同类别的偏好设置
preference_service.save_user_preferences(1, ui_preferences, "ui")
preference_service.save_user_preferences(1, notification_preferences, "notification")
preference_service.save_user_preferences(1, workspace_preferences, "workspace")

# 获取所有偏好设置
all_preferences = preference_service.get_all_user_preferences(1)
```

## 🎨 设计模式

### 服务层模式
- 每个服务类负责特定的业务逻辑
- 服务之间通过依赖注入和接口通信
- 统一的错误处理和日志记录

### 数据访问层
- 使用SQLAlchemy ORM进行数据库操作
- 统一的数据库连接管理
- 事务管理和连接池

### 外部API集成
- JSONPlaceholder API用于用户数据
- 缓存机制减少API调用
- 优雅的错误处理和重试机制

## 🧪 测试

### 运行示例
```bash
# 在backend目录下运行
python service/example_usage.py
```

### 测试覆盖
- 用户服务测试
- 偏好设置CRUD测试
- 笔记管理测试
- 待办事项管理测试
- 服务集成测试

## 📝 最佳实践

### 1. 错误处理
```python
try:
    result = service.operation()
    if result:
        print("操作成功")
    else:
        print("操作失败")
except Exception as e:
    print(f"发生错误: {e}")
```

### 2. 资源管理
```python
# 使用上下文管理器
with DatabaseClient() as db_client:
    service = SomeService(db_client)
    # 操作...
# 自动关闭连接
```

### 3. 数据验证
```python
# 验证用户存在
if not user_service.validate_user_exists(user_id):
    raise ValueError("用户不存在")

# 验证数据完整性
if not title or not content:
    raise ValueError("标题和内容不能为空")
```

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否运行
   - 验证环境变量配置
   - 检查用户权限

2. **API调用失败**
   - 检查网络连接
   - 验证JSONPlaceholder API状态
   - 检查用户ID范围（1-10）

3. **数据不一致**
   - 检查外键约束
   - 验证事务完整性
   - 检查数据类型匹配

### 调试技巧

1. **启用SQL日志**
   ```bash
   DB_ECHO=true
   ```

2. **使用调试模式**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **检查数据库状态**
   ```bash
   python core/database_core/test_db.py
   ```

## 📚 扩展开发

### 添加新服务
1. 创建模型类（继承BaseModel）
2. 创建服务类（实现业务逻辑）
3. 添加到__init__.py导出
4. 编写测试和文档

### 添加新功能
1. 在现有服务中添加方法
2. 更新相关模型（如需要）
3. 添加索引优化查询
4. 更新文档和示例

---

## 🎉 总结

Service层提供了完整的业务逻辑实现，包括：
- ✅ 用户管理（基于JSONPlaceholder API）
- ✅ 偏好设置管理（JSON格式存储）
- ✅ 笔记管理（支持标签和搜索）
- ✅ 待办事项管理（支持关联笔记）
- ✅ 数据统计和分析
- ✅ 完整的错误处理
- ✅ 资源管理和优化

现在您可以基于这个Service层构建更上层的应用，如Web API、命令行工具或图形界面。 