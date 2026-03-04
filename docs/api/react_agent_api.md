# ReAct 代理 API 设计

## 1. 端点

### WebSocket `/api/v1/chat/ws`
为用户查询启动一个 ReAct 代理会话。支持 WebSocket 双向通信以流式传输思维和行动。

#### 连接与请求
连接到 WebSocket 后，发送以下 JSON 消息：
```json
{
  "query": "比较 BFS 和 DFS 的时间复杂度。",
  "session_id": "optional_session_id",
  "history": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"}
  ],
  "model_config": {
    "temperature": 0.5,
    "max_tokens": 1024
  }
}
```

#### 响应 (流式)
API 通过 WebSocket 推送表示代理思维过程的 JSON 对象。

**事件类型:**
1. **`thought`**: 代理的内部推理。
   ```json
   {"type": "thought", "content": "我需要先查找 BFS 的时间复杂度。"}
   ```
2. **`tool_start`**: 代理准备调用工具。
   ```json
   {"type": "tool_start", "tool": "local_knowledge", "input": {"query": "BFS 时间复杂度"}}
   ```
3. **`tool_end`**: 工具执行完成。
   ```json
   {"type": "tool_end", "tool": "local_knowledge", "output": "BFS 复杂度是 O(V+E)..."}
   ```
4. **`answer`**: 最终答案的片段（流式）。
   ```json
   {"type": "answer", "content": "时间复杂度..."}
   ```
5. **`error`**: 系统错误。
   ```json
   {"type": "error", "content": "达到最大迭代次数。"}
   ```
6. **`done`**: 流结束。
   ```json
   {"type": "done"}
   ```

## 2. 工具接口 (内部)

### `LocalKnowledgeTool`
- **输入**: `{"query": "string"}`
- **输出**: `string` (来自 RAG 的摘要上下文)

### `WebSearchTool`
- **输入**: `{"query": "string"}`
- **输出**: `string` (搜索摘要)

### `CalculatorTool`
- **输入**: `{"expression": "string"}`
- **输出**: `string` (结果)
