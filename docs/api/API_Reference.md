# Role D: 问答与教师 Agent API 参考文档

## 1. 概述
本模块负责处理学生与 AI 教师 Agent 之间的所有实时交互，包括：
- **智能问答 (Intelligent QA)**: 基于课程知识图谱的 RAG 问答。
- **反馈循环 (Feedback Loop)**: 检测困惑度并触发补充讲解。
- **会话控制 (Session Control)**: 管理学习进度和状态。

**基础路径**: `/api/v1`

## 2. 认证 (计划中)
目前系统在开发阶段使用模拟用户 ID (`student_001`)。
未来实现将使用 Bearer Token (JWT)。
- **Header**: `Authorization: Bearer <token>`

## 3. 接口列表

### 3.1 聊天与问答 (Chat & QA)

#### WebSocket `/api/v1/chat/ws`
全双工聊天流式传输。用于实时发送查询并接收流式响应。

- **协议**: WebSocket
- **消息格式** (客户端 -> 服务端):
  ```json
  {
    "query": "解释牛顿第二定律",
    "session_id": "sess_123",
    "current_path": "mechanics/newton", // 可选，当前学习路径上下文
    "top_k": 3 // 可选，检索数量
  }
  ```

- **消息格式** (服务端 -> 客户端):
  服务端通过 WebSocket 流式发送 JSON 字符串，每条消息包含 `type` 和 `content`/`data`。

  **消息类型示例**:

  1. **Token (文本生成片段)**:
     ```json
     {"type": "token", "content": "牛"}
     ```
     ```json
     {"type": "token", "content": "顿"}
     ```

  2. **Sources (参考来源)**:
     ```json
     {
       "type": "sources",
       "data": [
         {
           "node_id": "n1",
           "content": "力等于质量乘以加速度...",
           "relevance_score": 0.95,
           "metadata": {"source": "textbook_ch2.pdf"}
         }
       ]
     }
     ```

  3. **Suggestions (后续建议 - 可选)**:
     ```json
     {"type": "suggestions", "content": ["F代表什么?", "m代表什么?"]}
     ```

  4. **Error (错误信息)**:
     ```json
     {"type": "error", "content": "无法连接到知识库。"}
     ```

  5. **Metrics (性能指标 - 可选)**:
     ```json
     {"type": "metrics", "data": {"speed": "20 tok/s", "cache_hit": true}}
     ```

  6. **MCP Tool Events (MCP 工具调用事件)**:
     - `tool_start`: 开始调用工具
     - `tool_result`: 工具执行完成
     - `tool_error`: 工具执行出错
     *(详见第 4 节)*

### 3.2 聊天会话管理 (Chat Sessions Management)

用于管理侧边栏的聊天历史记录。

#### GET `/api/v1/chat/sessions`
获取当前用户的聊天会话列表。

**响应**:
```json
[
  {
    "id": "chat_12345678",
    "title": "New Chat",
    "updated_at": "2023-10-27T10:00:00"
  }
]
```

#### POST `/api/v1/chat/sessions`
创建一个新的空白聊天会话。

**响应**:
```json
{
  "session_id": "chat_87654321"
}
```

#### GET `/api/v1/chat/history/{session_id}`
获取指定会话的完整聊天历史。

**响应**:
```json
[
  {
    "role": "user",
    "content": "Hello",
    "timestamp": "..."
  },
  {
    "role": "assistant",
    "content": "Hi there!",
    "sources": [...]
  }
]
```

#### POST `/api/v1/chat/history/{session_id}/truncate`
撤回消息（截断历史记录到指定索引）。

**请求**:
```json
{
  "index": 2
}
```

**响应**:
```json
{
  "status": "success"
}
```

### 3.3 学习会话 (Learning Sessions)

#### POST `/api/v1/chat/session/start`
开始学习会话。

**请求**:
```json
{
  "course_id": "phys101",
  "mode": "learning", // 或 "preview" (预习)
  "target_node_id": "n1"
}
```

**响应**:
```json
{
  "session_id": "sess_new_123",
  "status": "active",
  "message": "Session started"
}
```

#### GET `/api/v1/chat/session/{session_id}/preview`
检查视频生成任务状态（预习模式）。

**响应**:
```json
{
  "status": "completed", // processing, failed
  "video_url": "http://...",
  "progress": 100
}
```

### 3.4 系统与配置 (System & Config)

#### GET `/api/v1/chat/metrics`
获取当前缓存性能指标。

**响应**:
```json
{
  "hits": 10,
  "misses": 5,
  "total": 15,
  "hit_rate": 0.66
}
```

#### POST `/api/v1/chat/config/reload`
热重载 QA 服务配置（例如修改提示词或环境变量后）。

**响应**:
```json
{
  "status": "reloaded"
}
```

### 3.5 数学流式计算 (Math Streaming Calculation)

#### POST `/api/v1/chat/math/stream`
流式数学计算端点。用于实时生成代码并执行，返回流式结果。

- **协议**: HTTP/1.1 (Server-Sent Events)
- **请求头**: `Content-Type: application/json`
- **请求体**:
  ```json
  {
    "query": "计算矩阵[[1,2],[3,4]]和[[5,6],[7,8]]的乘积",
    "session_id": "sess_123"
  }
  ```

- **响应格式** (服务端 -> 客户端):
  服务端通过 Server-Sent Events (SSE) 流式发送数据，每条消息包含 `type` 和 `content`。

  **事件类型**:
  1. `code_delta`: 生成的代码片段。
  2. `execution_result`: 代码执行结果（通常是最后一条语句的返回值）。
  3. `execution_error`: 代码执行出错时的错误信息。
  4. `explanation_delta`: 对结果的解释文本片段。
  5. `[DONE]`: 流结束标志。

  **示例流**:
  ```text
  data: {"type": "code_delta", "content": "import numpy as np"}

  data: {"type": "code_delta", "content": "\na = np.array([[1,2],[3,4]])"}

  data: {"type": "execution_result", "content": "[[19. 22.],[43. 50.]]"}

  data: {"type": "explanation_delta", "content": "矩阵乘积的结果是"}

  data: [DONE]
  ```

```json
{
  "status": "success",
  "message": "Configuration reloaded."
}
```

### 3.5 学生画像 (Student Profile)

#### GET `/api/v1/student/profile`
获取当前学生画像。

#### POST `/api/v1/student/profile`
更新学生画像。

**请求**:
```json
{
  "learning_style": "visual", // visual (视觉型), auditory (听觉型), kinesthetic (动觉型)
  "knowledge_level": "beginner",
  "interests": ["physics", "math"]
}
```

## 4. MCP 服务调用与前端展示规范

本章节定义了基于 Model Context Protocol (MCP) 的工具调用标准及前端渲染要求。

### 4.1 核心概念
系统采用 MCP 协议统一管理工具调用（如搜索、计算、RAG 检索）。每个工具调用都遵循 `Request` -> `Execution` -> `Result` 的生命周期，并通过 WebSocket 实时推送状态。

### 4.2 消息数据结构

#### 4.2.1 工具调用开始 (`tool_start`)
当 Agent 决定调用一个工具时触发。

```json
{
  "type": "tool_start",
  "tool_call_id": "call_123456", // 唯一标识本次调用
  "tool_name": "calculator",     // 工具名称
  "tool_icon": "🧮",             // (可选) 前端展示图标
  "inputs": {                    // 工具输入参数
    "expression": "sqrt(256) + 10"
  },
  "description": "正在计算 256 的平方根加 10..." // 人类可读的描述
}
```

#### 4.2.2 工具调用结果 (`tool_result`)
工具执行成功并返回结果时触发。

```json
{
  "type": "tool_result",
  "tool_call_id": "call_123456",
  "tool_name": "calculator",
  "status": "success",
  "output": "26",                // 工具输出结果（可能是文本、JSON 或 Markdown）
  "render_type": "text",         // 建议的前端渲染类型: text, markdown, json, table, chart
  "execution_time": 0.45         // 执行耗时（秒）
}
```

#### 4.2.3 工具调用错误 (`tool_error`)
工具执行失败时触发。

```json
{
  "type": "tool_error",
  "tool_call_id": "call_123456",
  "tool_name": "calculator",
  "status": "error",
  "error_message": "Invalid syntax",
  "error_details": "SyntaxError: unexpected EOF while parsing"
}
```

### 4.3 前端展示标准 (UI/UX)

前端应通过统一的 **"Thought Chain Component" (思维链组件)** 来展示 MCP 调用过程。

#### 4.3.1 展示状态机
1.  **Pending (进行中)**:
    - 展示加载动画 (Spinner)。
    - 显示 `description` 或 "正在调用 [工具名]..."。
    - *样式建议*: 灰色或蓝色半透明背景，呼吸灯效果。

2.  **Success (成功)**:
    - 展示成功图标 (✅)。
    - 默认折叠详情，仅展示工具名称和简短结果摘要。
    - 用户点击可展开查看完整的 `inputs` 和 `output`。
    - *样式建议*: 绿色边框或浅绿色背景。

3.  **Error (错误)**:
    - 展示错误图标 (❌)。
    - 显示红色错误简述。
    - 提供 "Retry" (重试) 按钮（如果业务逻辑支持）。
    - *样式建议*: 红色背景或边框。

#### 4.3.2 特殊渲染支持 (`render_type`)
根据 `tool_result` 中的 `render_type` 字段，前端应支持富媒体渲染：

- **`text`**: 纯文本展示（默认）。
- **`markdown`**: 渲染 Markdown 格式（如搜索结果列表）。
- **`json`**: 使用代码高亮组件展示 JSON 数据（适合调试或开发者模式）。
- **`table`**: 将 CSV 或数组数据渲染为表格。
- **`chart`**: 如果返回数据包含绘图配置（如 ECharts/Chart.js 配置），渲染为图表。
- **`image`**: 如果返回 URL 或 Base64，渲染为图片。

#### 4.3.3 交互建议
- **思维链折叠**: 默认情况下，当 Agent 完成回答后，所有的中间 MCP 调用步骤应自动折叠为一个 "思考过程" (Thought Process) 摘要，用户点击可展开查看完整链路。
- **引用跳转**: 如果最终答案引用了某个工具调用的结果（如搜索来源），点击引用标号应自动滚动并高亮对应的工具调用卡片。
