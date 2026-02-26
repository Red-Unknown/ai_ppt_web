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

#### POST `/api/v1/chat/chat`
向 Agent 发送查询、反馈或指令。

**请求体** (`application/json`):
```json
{
  "query": "解释牛顿第二定律",
  "session_id": "sess_123",
  "current_path": "mechanics/newton",
  "top_k": 3
}
```

**响应** (`application/json`):
```json
{
  "answer": "牛顿第二定律指出 F=ma...",
  "session_id": "sess_123",
  "action": "QA_ANSWER", // 或 SUPPLEMENT (补讲), FALLBACK_VIDEO (视频兜底)
  "source_nodes": [
    {
      "node_id": "n1",
      "content": "力等于质量乘以加速度...",
      "relevance_score": 0.95
    }
  ],
  "action_data": {} // 特定动作的可选数据
}
```

### 3.2 实时流式传输 (Real-time Streaming)

#### WebSocket `/api/v1/chat/ws`
全双工聊天流式传输。
- **协议**: WebSocket
- **消息格式** (客户端 -> 服务端): 同 `POST /chat/chat` 请求体。
- **消息格式** (服务端 -> 客户端):
  - `{"type": "start", "action": "QA_ANSWER"}`
  - `{"type": "token", "content": "牛"}`
  - `{"type": "token", "content": "顿"}`
  - `{"type": "sources", "data": [...]}`
  - `{"type": "suggestions", "content": ["F代表什么?", "m代表什么?"]}`
  - `{"type": "metrics", "data": {"speed": "...", "cache_stats": ...}}`
  - `{"type": "end"}`

#### GET `/api/v1/chat/sse`
Server-Sent Events (SSE) 流式传输备选方案。
- **查询参数**: `query`, `session_id`, `current_path`
- **格式**: `data: {...}\n\n` (JSON 对象同 WebSocket)

### 3.3 系统与配置 (System & Config)

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
  "status": "success",
  "message": "配置已重载。"
}
```

### 3.4 会话 (Sessions)

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
