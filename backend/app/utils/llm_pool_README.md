# LLM 连接池 (LLMPool)

用于管理和复用 LLM 客户端连接的连接池模块。

## 功能特性

- 连接池容量：最大 20 个连接，最小空闲 5 个
- 线程安全：支持多线程并发获取和释放
- 配置参数化：支持自定义最大连接数、超时时间等
- 健康检查：定期检测连接可用性
- 状态监控：实时查看活跃/空闲连接数
- 资源释放：应用关闭时正确释放所有资源

## 快速开始

### 初始化

```python
from backend.app.utils.llm_pool import initialize_pool, get_llm_client, release_llm_client

# 初始化连接池（推荐在应用启动时调用）
initialize_pool()
```

### 使用方式

#### 方式 1：手动获取和释放

```python
client = get_llm_client("qa")
try:
    # 使用 client...
    response = await client.ainvoke([HumanMessage(content="Hello")])
finally:
    release_llm_client(client)
```

#### 方式 2：上下文管理器（推荐）

```python
from backend.app.utils.llm_pool import LLMPoolContext

with LLMPoolContext("qa") as client:
    # 使用 client...
    response = await client.ainvoke([HumanMessage(content="Hello")])
# 自动释放
```

### 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| max_connections | 20 | 最大连接数 |
| min_idle_connections | 5 | 最小空闲连接数 |
| connection_timeout | 30.0 | 获取连接超时（秒） |
| idle_timeout | 300.0 | 空闲连接超时（秒） |
| health_check_interval | 60.0 | 健康检查间隔（秒） |

```python
from backend.app.utils.llm_pool import LLMPoolConfig, initialize_pool

config = LLMPoolConfig(
    max_connections=10,
    min_idle_connections=2,
    connection_timeout=60.0,
)
initialize_pool(config)
```

### 支持的场景

| 场景 | 说明 |
|------|------|
| qa | 问答场景 |
| reasoner | 推理场景 |
| summary | 摘要场景 |
| translation | 翻译场景 |
| qa_kimi | Kimi 模型 |
| qa_gpt | GPT 模型 |

### 查看状态

```python
from backend.app.utils.llm_pool import get_pool_status

status = get_pool_status()
print(status)
# {
#     'initialized': True,
#     'scenarios': {
#         'qa': {'active_connections': 1, 'idle_connections': 4, 'total_connections': 5},
#         ...
#     }
# }
```

### 关闭连接池

```python
from backend.app.utils.llm_pool import shutdown_pool

shutdown_pool()
```

## 在 QAService 中使用

QAService 已集成连接池，会自动初始化：

```python
from backend.app.services.qa.service import QAService

qa_service = QAService()
# 连接池会在首次使用时自动初始化
```
