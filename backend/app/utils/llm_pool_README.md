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

### 使用 model 参数（推荐方式）

#### 获取 Qwen 客户端

```python
# 获取 Qwen 文本模型客户端
client = get_llm_client(model="qwen")

# 获取 Qwen VL 视觉模型客户端（支持图片识别）
client = get_llm_client(model="qwen-vl")

# 使用上下文管理器
with LLMPoolContext(model="qwen") as client:
    response = await client.ainvoke([HumanMessage(content="Hello")])
```

#### 向后兼容：使用默认 DeepSeek 客户端

```python
# 不指定 model 参数，默认返回 DeepSeek 客户端
client = get_llm_client()

# 显式指定 deepseek 模型
client = get_llm_client(model="deepseek")

# 使用旧版 scenario 方式（仍支持）
client = get_llm_client("qa")
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

### 支持的模型

| 模型标识 | 说明 | 支持场景 |
|----------|------|----------|
| qwen | Qwen 文本模型 (qwen-turbo) | qwen, qa_qwen, reasoner_qwen 等 |
| qwen-vl | Qwen VL 视觉模型 (qwen-vl-plus)，支持图片识别 | qwen_vision, qa_qwen_vision 等 |
| deepseek | DeepSeek 文本模型（默认） | qa, reasoner, summary, translation |
| gpt | OpenAI GPT-4o | qa_gpt, reasoner_gpt 等 |
| kimi | 月之暗面 Kimi 模型 | qa_kimi, reasoner_kimi 等 |

### 环境变量配置

API Key 读取优先级：**项目根目录 .env 文件 > 系统环境变量**

在 `.env` 文件中配置：

```bash
# DeepSeek 配置
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat

# Qwen 配置（阿里云通义千问）
QWEN_API_KEY=your-qwen-api-key
QWEN_MODEL=qwen-turbo
QWEN_VISION_MODEL=qwen-vl-plus

# Kimi 配置（可选）
KIMI_API_KEY=your-kimi-api-key

# OpenAI 配置（可选）
OPENAI_API_KEY=your-openai-api-key
```

### 异常处理

连接池定义了以下异常类：

```python
from backend.app.utils.llm_pool import (
    PoolError,
    PoolTimeoutError,
    LLMConfigurationError,
)

try:
    client = get_llm_client(model="qwen")
except LLMConfigurationError as e:
    # API Key 未配置
    print(f"请配置 API Key: {e}")
except PoolTimeoutError as e:
    # 获取连接超时
    print(f"连接池超时: {e}")
```

### 查看状态

```python
from backend.app.utils.llm_pool import get_pool_status

status = get_pool_status()
print(status)
# {
#     'initialized': True,
#     'scenarios': {
#         'qa': {'active_connections': 1, 'idle_connections': 4, 'total_connections': 5},
#         'qwen': {'active_connections': 0, 'idle_connections': 5, 'total_connections': 5},
#         'qwen_vision': {'active_connections': 0, 'idle_connections': 5, 'total_connections': 5},
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
