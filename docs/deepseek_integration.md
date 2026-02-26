# DeepSeek 集成与优化指南

## 1. DeepSeek API 集成

我们将 DeepSeek V3 (deepseek-chat) 集成作为 QA 服务的核心 LLM。

### 1.0 后端启动

设置 API Key 并启动后端服务。

- **Windows (PowerShell)**
    1) `$env:DEEPSEEK_API_KEY="sk-your-key"` (当前终端生效)
    2) `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
  
- **Linux/MacOS (bash/zsh)**
    1) `export DEEPSEEK_API_KEY="sk-your-key"`
    2) `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`

**接口列表**:
- WebSocket: `/api/v1/chat/ws`
- SSE: `/api/v1/chat/sse?query=...&session_id=...&current_path=...`
- 指标: `/api/v1/chat/metrics`
- 热重载: `POST /api/v1/chat/config/reload`

**手动测试提示**:
- 快速缓存路径: 查询 `课程介绍`
- RAG 路径: 查询 `牛顿第二定律是什么？`

### 1.1 配置

在 `.env` 文件中配置以下环境变量:

```bash
# DeepSeek API Configuration
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MAX_TOKENS=2048
DEEPSEEK_TEMPERATURE=0.7
```

### 1.2 基于场景的策略

为了优化成本和性能，我们针对不同场景使用不同的配置:

| 场景 | 模型 | 温度 (Temperature) | 最大 Tokens | 用途 |
| :--- | :--- | :--- | :--- | :--- |
| **qa** | deepseek-chat | 0.7 | 2048 | 标准问答 |
| **summary** | deepseek-chat | 0.3 | 4096 | 内容总结 (更确定性) |
| **translation** | deepseek-chat | 0.1 | 4096 | 语言翻译 (高度确定性) |

### 1.3 热重载

你可以在不重启服务器的情况下更新配置。
1. 更新 `.env` 文件或环境变量。
2. 调用重载接口:
   ```bash
   POST /api/v1/chat/config/reload
   ```

## 2. 本地磁盘缓存设计

受 DeepSeek 上下文缓存的启发，我们实现了客户端侧的 **本地磁盘缓存**，以降低重复查询的 API 成本和延迟。

### 2.1 架构

*   **存储**: SQLite (`cache.db`)
*   **键**: SHA256(Prompt + Parameters)
*   **值**: 完整文本响应
*   **驱逐策略**: 基于 TTL (生存时间) (默认: 24 小时)。LRU 式访问追踪。

### 2.2 工作流

1.  **请求**: 用户发送查询。
2.  **意图缓存检查**: 检查内存高速缓存 (针对静态 FAQ)。
3.  **磁盘缓存检查**: 检查 SQLite `llm_cache` 表。
    *   **命中**: 立即返回缓存响应。(延迟 < 10ms)
    *   **未命中**: 调用 DeepSeek API。
4.  **更新**: 将新的 API 响应保存到 SQLite。

### 2.3 指标

通过 `GET /api/v1/chat/metrics` 监控缓存性能:

```json
{
  "hits": 45,
  "misses": 120,
  "total_requests": 165,
  "hit_rate": "27.27%"
}
```

## 3. 提示词管理

提示词在 `QAService` 内部进行版本控制。
*   **default**: 标准角色。
*   **v2_creative**: 更有趣的角色，用于提高参与度。

未来的工作可以将这些移至 YAML/JSON 文件以进行动态加载。
