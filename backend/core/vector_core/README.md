# Vector Core - Chroma Vector Database with OpenAI Embeddings

这个模块提供了一个基于 Chroma 向量数据库的完整解决方案，使用 OpenAI 的嵌入模型进行文本向量化存储和检索。

## 功能特性

1. **文本向量存储** - 将文本转换为向量并存储在本地数据库中
2. **自定义元数据支持** - 为每个文档添加自定义元数据信息
3. **元数据过滤查询** - 基于元数据条件进行精确查询
4. **语义相似性查询** - 基于文本语义进行相似性搜索
5. **用户隔离** - 每个用户拥有独立的数据集合
6. **OpenAI 嵌入模型** - 使用 OpenAI 的 text-embedding-3-small 模型
7. **源标签筛选删除** - 基于源标签进行批量删除操作
8. **本地持久化存储** - 数据本地存储，支持重启后数据恢复

## 安装依赖

确保已安装以下依赖项：

```bash
pip install chromadb>=0.4.22 openai>=1.0.0 numpy>=1.26.0 pydantic>=2.0.0
```

## 环境变量配置

创建 `.env` 文件并设置以下环境变量：

```env
# 必需配置
OPENAI_API_KEY=your-openai-api-key-here

# 可选配置
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_PREFIX=ai_assistant
VECTOR_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7
DEFAULT_QUERY_LIMIT=10
```

## 快速开始

### 1. 初始化客户端

```python
from backend.core.vector_core import ChromaVectorClient, VectorConfig

# 从环境变量加载配置
config = VectorConfig.from_env()
client = ChromaVectorClient(config)
```

### 2. 添加文档

```python
from backend.core.vector_core import VectorDocument

# 创建文档
document = VectorDocument(
    id="doc_1",
    text="Python is a powerful programming language",
    metadata={"category": "programming", "language": "python"},
    user_id="user_123",
    source="tutorial_docs"
)

# 添加到向量数据库
doc_id = client.add_document(document)
```

### 3. 查询文档

```python
from backend.core.vector_core import VectorQuery

# 创建查询
query = VectorQuery(
    query_text="programming language",
    user_id="user_123",
    limit=5,
    similarity_threshold=0.5
)

# 执行查询
results = client.query_documents(query)
for result in results:
    print(f"ID: {result.id}, Score: {result.score:.3f}")
    print(f"Text: {result.text}")
```

### 4. 元数据过滤查询

```python
# 基于元数据过滤
query_filtered = VectorQuery(
    query_text="programming",
    user_id="user_123",
    metadata_filter={"category": "programming"},
    limit=10
)

results = client.query_documents(query_filtered)
```

### 5. 删除文档

```python
from backend.core.vector_core import VectorDeleteFilter

# 按源标签删除
delete_filter = VectorDeleteFilter(
    user_id="user_123",
    source_filter="tutorial_docs"
)

deleted_count = client.delete_documents(delete_filter)
```

## 主要类和方法

### ChromaVectorClient

主要的向量数据库客户端类。

#### 方法：

- `add_document(document: VectorDocument) -> str` - 添加单个文档
- `add_documents(documents: List[VectorDocument]) -> List[str]` - 批量添加文档
- `query_documents(query: VectorQuery) -> List[VectorQueryResult]` - 查询文档
- `delete_documents(delete_filter: VectorDeleteFilter) -> int` - 删除文档
- `get_document_by_id(document_id: str, user_id: str) -> Optional[VectorQueryResult]` - 按ID获取文档
- `get_stats(user_id: str) -> VectorStats` - 获取用户统计信息
- `update_document(document_id: str, user_id: str, text: str, metadata: Dict) -> bool` - 更新文档
- `clear_user_data(user_id: str) -> bool` - 清除用户所有数据
- `health_check() -> Dict[str, Any]` - 健康检查

### VectorDocument

文档数据模型：

```python
VectorDocument(
    id: str,                    # 文档ID
    text: str,                  # 文档内容
    metadata: Dict[str, Any],   # 自定义元数据
    user_id: str,               # 用户ID
    source: Optional[str],      # 源标签
    created_at: datetime        # 创建时间
)
```

### VectorQuery

查询参数模型：

```python
VectorQuery(
    query_text: str,                      # 查询文本
    user_id: str,                         # 用户ID
    limit: int = 10,                      # 结果数量限制
    similarity_threshold: float = None,   # 相似度阈值
    metadata_filter: Dict = None,         # 元数据过滤
    source_filter: str = None,            # 源标签过滤
    include_metadata: bool = True,        # 是否包含元数据
    include_distances: bool = True        # 是否包含距离信息
)
```

### VectorDeleteFilter

删除过滤器模型：

```python
VectorDeleteFilter(
    user_id: str,                         # 用户ID
    source_filter: str = None,            # 源标签过滤
    metadata_filter: Dict = None,         # 元数据过滤
    document_ids: List[str] = None        # 特定文档ID列表
)
```

## 完整示例

查看 `example_usage.py` 文件获取完整的使用示例，包括：

- 文档添加和批量添加
- 基本查询和过滤查询
- 用户隔离测试
- 文档更新和删除
- 统计信息获取
- 数据清理

## 运行示例

要运行示例，请从 `backend` 目录执行以下命令：

```bash
python -m core.vector_core.example_usage
```

这会将 `example_usage.py` 作为模块运行，确保所有内部导入都能正常工作。

## 注意事项

1. **OpenAI API Key** - 确保设置了有效的 OpenAI API Key
2. **数据持久化** - 数据存储在本地，重启后数据保留
3. **用户隔离** - 每个用户的数据完全隔离，不会相互影响
4. **元数据限制** - 元数据值仅支持 str、int、float、bool 类型
5. **文本长度** - 建议单个文档不超过 8000 个字符以确保最佳性能

## 故障排除

### 常见问题

1. **OpenAI API Key 错误** - 检查环境变量是否正确设置
2. **权限问题** - 确保有权限创建和写入数据库目录
3. **依赖版本冲突** - 确保使用推荐的依赖版本

### 日志记录

模块使用标准的 Python logging 模块。可以通过设置日志级别来调试问题：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 性能优化

1. **批量操作** - 尽量使用 `add_documents()` 进行批量添加
2. **合理的查询限制** - 设置合适的 `limit` 值
3. **相似度阈值** - 使用 `similarity_threshold` 过滤低相关性结果
4. **定期清理** - 定期删除不需要的文档以保持性能 