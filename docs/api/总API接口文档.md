

# API 接口文档 v1.4

## 文档说明

本文档描述了基于树形知识图谱的在线教育辅助系统的后端接口，涵盖鉴权、课程管理、学习会话、预览任务及增强的聊天互动能力。

* **版本**：v1.4（新增数据库查询接口）
* **基础路径**：`/api/v1`
* **鉴权方式**：Bearer Token (JWT)
* **时间格式**：ISO 8601（例如 `2026-03-20T10:00:00Z`）

---

## 0. 全局约定（响应与错误规范）

### 0.1 统一响应结构

除极少数简单健康检查外，所有接口的响应统一包裹为：

```json
{
  "code": "OK",
  "message": "操作成功",
  "data": { ... },
  "request_id": "req_20260320_001"
}
```

### 0.2 错误响应结构

发生错误（HTTP 状态码 ≥ 400）时，响应体约定为：

```json
{
  "code": "AUTH_INVALID_TOKEN",
  "message": "访问令牌无效或已过期",
  "request_id": "req_20260320_002",
  "details": {
    "reason": "token_expired"
  }
}
```

---

## 1. 聊天会话管理 (Chat Sessions) [NEW]

用于管理通用的问答对话历史，支持多轮对话、回滚与持久化。

### 1.1 获取会话列表
**GET /chat/sessions**

* **描述**：获取当前用户的聊天会话列表。
* **响应 (200 OK)**：
  ```json
  {
    "code": "OK",
    "data": [
      {
        "id": "chat_a1b2c3d4",
        "title": "关于牛顿定律的讨论",
        "updated_at": "2026-03-20T10:05:00Z"
      }
    ]
  }
  ```

### 1.2 创建新会话
**POST /chat/sessions**

* **描述**：创建一个新的空白聊天会话。
* **响应 (200 OK)**：
  ```json
  {
    "code": "OK",
    "data": {
      "session_id": "chat_e5f6g7h8"
    }
  }
  ```

### 1.3 获取会话历史
**GET /chat/history/{session_id}**

* **描述**：获取指定会话的完整聊天记录。
* **响应 (200 OK)**：
  ```json
  {
    "code": "OK",
    "data": [
      {
        "role": "user",
        "content": "什么是动量？",
        "timestamp": "..."
      },
      {
        "role": "assistant",
        "content": "动量是质量与速度的乘积...",
        "timestamp": "..."
      }
    ]
  }
  ```

### 1.4 截断会话历史 (Undo)
**POST /chat/history/{session_id}/truncate**

* **描述**：将会话历史回滚到指定索引（用于“撤回”或“重新生成”功能）。
* **请求体**：
  ```json
  {
    "index": 4 // 保留 0-3 条消息，删除索引 4 及之后的消息
  }
  ```
* **响应 (200 OK)**：
  ```json
  {
    "code": "OK",
    "message": "History truncated"
  }
  ```

---

## 2. 实时问答与推理 (WebSocket) [UPDATED]

**URL**: `/api/v1/chat/ws`

### 2.1 交互协议

客户端发送 JSON：
```json
{
  "query": "推导相对论公式",
  "session_id": "chat_a1b2c3d4",
  "model": "deepseek-reasoner" // 可选: deepseek-chat, deepseek-reasoner
}
```

服务端下发 JSON 事件流：

#### 事件类型 (Type)

| type | 说明 | Payload 示例 |
| :--- | :--- | :--- |
| `start` | 开始生成 | `{"action": "QA_ANSWER"}` |
| `status` | 状态更新 | `{"content": "正在检索知识库..."}` |
| `reasoning` | **[NEW]** 推理内容片段 | `{"content": "首先考虑..."}` |
| `reasoning_end` | **[NEW]** 推理结束信号 | `{}` |
| `token` | 回答内容片段 | `{"content": "E=mc^2"}` |
| `sources` | 引用来源 | `{"data": [...]}` |
| `end` | 生成结束 | `{}` |
| `error` | 错误信息 | `{"content": "搜索超时"}` |

### 2.2 推理模式 (Reasoner Mode)

当使用 `deepseek-reasoner` 模型时，服务端会先推送 `reasoning` 事件流，包含模型的思考过程。
前端应渲染一个折叠组件展示此内容。
当收到 `reasoning_end` 事件时，前端应在 0.5s 后自动折叠思考框。

---

## 3. 学习会话与预览 (Learning & Preview)

### 3.1 启动学习/预览
**POST /session/start**

* **请求体**：
  ```json
  {
    "course_id": "c_1001",
    "mode": "learn", // 或 "preview"
    "target_node_id": "n_502"
  }
  ```
* **响应**：
  ```json
  {
    "code": "OK",
    "data": {
      "session_id": "sess_learn_7731",
      "task_id": "task_..." // 仅 preview 模式返回
    }
  }
  ```

### 3.2 查询预览状态
**GET /session/{session_id}/preview**

* **响应**：
  ```json
  {
    "code": "OK",
    "data": {
      "status": "processing", // processing, completed, failed
      "progress": 45,
      "video_url": "http://..."
    }
  }
  ```

---

## 4. 内部策略说明 (Internal Strategies)

### 4.1 单一 Chat 缓存 (Single Chat Cache)
* **机制**：在 Session 生命周期内，对相同语义的问题（Fingerprint）缓存检索结果。
* **目的**：减少重复检索开销，提升响应速度。
* **生命周期**：随 Session 销毁。

### 4.2 联网搜索限制 (Web Search Limiting)
* **限制**：每个 Session 仅允许触发一次联网搜索。
* **标志**：`search_used` (Boolean)。一旦触发，后续请求禁用搜索工具。
* **并发**：搜索时并行抓取 Top 5 结果（3s 超时）。
* **熔断**：若搜索结果质量低（Hit Rate < Threshold），返回固定提示语。

---

## 5. 数据库查询接口 (Database Query) [NEW]

提供对持久化问答记录和学习进度的查询能力。

### 5.1 查询会话问答记录
**GET /chat/db/qa-records/{session_id}**

* **描述**：获取指定会话的所有持久化问答记录（从数据库查询）。
* **参数**：
  * `session_id` (路径参数)：会话ID
  * `limit` (查询参数，可选)：返回记录数量，默认20
* **响应 (200 OK)**：
  ```json
  {
    "code": "OK",
    "data": [
      {
        "answer_id": 1,
        "session_id": "session_123",
        "user_id": "student_001",
        "question_text": "什么是极限？",
        "answer_text": "极限是微积分的基本概念...",
        "question_type": "FACTOID",
        "cited_node_id": "node_001",
        "sources": [
          {
            "node_id": "node_001",
            "page_num": 5,
            "content": "极限的定义..."
          }
        ],
        "created_at": "2026-04-13T10:30:00"
      }
    ]
  }
  ```

### 5.2 查询学习进度
**GET /chat/db/learning-progress/{session_id}**

* **描述**：获取指定会话的学习进度（从数据库查询）。
* **参数**：
  * `session_id` (路径参数)：会话ID
  * `user_id` (查询参数，可选)：用户ID，默认 "student_001"
* **响应 (200 OK)**：
  ```json
  {
    "code": "OK",
    "data": {
      "track_id": "student_001_session_123",
      "user_id": "student_001",
      "session_id": "session_123",
      "lesson_id": "lesson_001",
      "current_node_id": "node_005",
      "current_path": "/chapter1/section2",
      "current_topic": "极限",
      "confusion_count": 2,
      "mastery": {
        "极限": 0.65,
        "导数": 0.3
      },
      "last_position_seconds": 120,
      "progress_percent": 15.5,
      "adjust_type": "normal",
      "needs_supplement": false,
      "last_operate_time": "2026-04-13T10:35:00"
    }
  }
  ```
* **无记录响应**：
  ```json
  {
    "code": "OK",
    "data": null,
    "message": "No progress record found"
  }
  ```
