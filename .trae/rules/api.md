---
alwaysApply: true
---
## 7. API 与接口设计规范 (API Design)

### 7.1 异步任务模式 (Async Task Pattern)
针对赛题中“课件解析耗时 ≤ 2分钟”的要求，相关接口必须设计为**异步非阻塞**。

- **提交任务接口**：
    - `POST /api/v1/parser/upload`
    - **Return**: `{ "task_id": "uuid", "status": "pending" }` (HTTP 202 Accepted)
- **查询状态接口**：
    - `GET /api/v1/parser/tasks/{task_id}`
    - **Return**: `{ "status": "processing", "progress": 45, "result": null }`
- **获取结果接口**：
    - 当状态为 `completed` 时，`result` 字段返回 CIR JSON 数据的 URL 或 ID。

### 7.2 接口定义标准
- **URL 风格**：RESTful, 名词复数 (e.g., `/courses/{id}/chapters`).
- **数据格式**：Request/Response Body 必须使用 JSON。
- **错误响应**：
    ```json
    {
      "code": 400,
      "message": "Invalid file format",
      "data": null
    }
    ```
- **文档优先**：修改接口前，必须先更新 OpenAPI (Swagger) 定义或与前端协商。