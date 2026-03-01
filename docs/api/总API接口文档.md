# API 接口文档 v1.2

## 文档说明

本文档描述了基于树形知识图谱的在线教育辅助系统的后端接口，并补充了全局错误规范、会话语义、预览任务与 RAG 能力等设计约定。

* **版本**：v1.2（新增全局错误规范、刷新机制、预览/学习会话拆分等）  
* **基础路径**：`/api/v1`  
* **鉴权方式**：Bearer Token (JWT)  
* **时间格式**：除特别说明外，所有时间字段均为 ISO 8601（例如 `2026-03-20T10:00:00Z`）  
* **ID 规范**：  
  * 课程：`course_id`，如 `c_1001`  
  * 知识点节点：`node_id`，如 `n_502`  
  * 会话：`session_id`，如 `sess_learn_7731`  
  * 预览任务：`preview_task_id`，如 `pt_992`  

---

## 0. 全局约定（响应与错误规范）

### 0.1 统一响应结构

除极少数简单健康检查外，所有接口的响应统一包裹为：

```json
{
  "code": "OK",
  "message": "登录成功",
  "data": { ... },
  "request_id": "req_20260320_001"
}
```

* **`code`**：业务状态码，字符串，成功时约定为 `"OK"`。  
* **`message`**：人类可读的简要说明。  
* **`data`**：业务数据载荷，结构由各接口自定义。  
* **`request_id`**：后端生成的请求 ID，所有日志必须携带此字段，便于排查问题。  

### 0.2 错误响应结构

发生错误（HTTP 状态码 ≥ 400）时，响应体约定为：

```json
{
  "code": "AUTH_INVALID_TOKEN",
  "message": "访问令牌无效或已过期",
  "request_id": "req_20260320_002",
  "details": {
    "reason": "token_expired",
    "expired_at": "2026-03-20T09:00:00Z"
  }
}
```

推荐的业务错误码示例（非穷举）：

* **认证/权限相关**：`AUTH_INVALID_TOKEN`, `AUTH_EXPIRED_TOKEN`, `AUTH_FORBIDDEN_ROLE`  
* **参数/资源相关**：`BAD_REQUEST`, `VALIDATION_FAILED`, `RESOURCE_NOT_FOUND`  
* **会话/任务相关**：`SESSION_NOT_FOUND`, `PREVIEW_TASK_FAILED`, `PREVIEW_TASK_EXPIRED`  
* **系统相关**：`INTERNAL_ERROR`, `UPSTREAM_TIMEOUT`, `SERVICE_UNAVAILABLE`  

HTTP 状态码与业务错误码的典型对应关系：

* `400 Bad Request` → `BAD_REQUEST` / `VALIDATION_FAILED`  
* `401 Unauthorized` → `AUTH_INVALID_TOKEN` / `AUTH_EXPIRED_TOKEN`  
* `403 Forbidden` → `AUTH_FORBIDDEN_ROLE`  
* `404 Not Found` → `RESOURCE_NOT_FOUND` / `SESSION_NOT_FOUND`  
* `409 Conflict` → 资源冲突类错误  
* `422 Unprocessable Entity` → 复杂参数校验失败  
* `429 Too Many Requests` → 限流  
* `500/502/503` → `INTERNAL_ERROR` / `SERVICE_UNAVAILABLE`  

---

## 1. 鉴权模块 (Authentication)

所有受保护接口需在 Header 中携带 `Authorization: Bearer <access_token>`。

### 1.1 获取访问令牌（登录）

**POST /auth/login**

* **请求体**：
  
  ```json
  {
    "username": "teacher_01",
    "password": "password123"
  }
  ```

* **响应 (200 OK)**：
  
  ```json
  {
    "code": "OK",
    "message": "登录成功",
    "request_id": "req_20260320_010",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIs...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
      "token_type": "bearer",
      "expires_in": 3600,
      "refresh_expires_in": 2592000,
      "user": {
        "id": "u_1001",
        "role": "teacher"
      }
    }
  }
  ```

> 如不希望实现 refresh 机制，则应在文档中明确：不返回 `refresh_token`，access 过期后只能重新登录，并描述前端应跳转登录页或静默重登录的策略。

### 1.2 刷新访问令牌

**POST /auth/refresh**

* **描述**：使用 `refresh_token` 获取新的 `access_token`，用于长会话场景。  

* **请求体**：
  
  ```json
  {
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }
  ```

* **响应 (200 OK)**：
  
  ```json
  {
    "code": "OK",
    "message": "刷新成功",
    "request_id": "req_20260320_011",
    "data": {
      "access_token": "new_access_token",
      "expires_in": 3600
    }
  }
  ```

* **错误示例 (401 Unauthorized)**：`code = "AUTH_EXPIRED_REFRESH_TOKEN"` 或 `AUTH_INVALID_TOKEN`。  

### 1.3 注销 / 撤销令牌

**POST /auth/logout**

* **描述**：注销当前登录会话，可选同时撤销对应的 refresh token（用于踢下线、更改密码后强制下线等）。  

* **请求头**：`Authorization: Bearer <access_token>`  

* **请求体（可选）**：
  
  ```json
  {
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }
  ```

* **响应 (200 OK)**：
  
  ```json
  {
    "code": "OK",
    "message": "已注销",
    "request_id": "req_20260320_012",
    "data": {}
  }
  ```

---

## 2. 课程会话与视频预览 (Sessions & Preview)

> 说明：为避免一个 endpoint 中混合两种语义（学习会话 vs 预览任务），推荐拆分为两个资源；原有 `POST /sessions/start` 可作为兼容接口保留并标记为 **Deprecated**。

### 2.1 启动学习会话（学生）

**POST /learning-sessions**

* **请求头**：`Authorization: Bearer <token>`（角色需为 `student`）  

* **请求体**：
  
  ```json
  {
    "course_id": "c_1001",
    "start_node_id": "n_502"
  }
  ```

* **响应 (201 Created)**：
  
  ```json
  {
    "code": "OK",
    "message": "学习会话已创建",
    "request_id": "req_20260320_020",
    "data": {
      "session_id": "sess_learn_7731",
      "course_id": "c_1001",
      "start_node": { }
    }
  }
  ```

### 2.2 创建视频预览任务（教师）

**POST /preview-tasks**

* **请求头**：`Authorization: Bearer <token>`（角色需为 `teacher`）  

* **请求体**：
  
  ```json
  {
    "course_id": "c_1001",
    "target_node_id": "n_502",
    "force_regenerate": false
  }
  ```

* **响应 (202 Accepted)**：
  
  ```json
  {
    "code": "OK",
    "message": "视频预览生成任务已提交",
    "request_id": "req_20260320_021",
    "data": {
      "preview_task_id": "pt_992",
      "session_id": "sess_preview_8821"
    }
  }
  ```

### 2.3 查询视频预览任务状态

**GET /preview-tasks/{preview_task_id}**

* **描述**：查询异步生成的视频预览任务状态，支持缓存策略。  

* **请求头**：`Authorization: Bearer <token>`  

* **响应 (200 OK)**：
  
  ```json
  {
    "code": "OK",
    "message": "查询成功",
    "request_id": "req_20260320_022",
    "data": {
      "status": "processing",
      "progress": 45,
      "eta_seconds": 15,
      "video_url": null,
      "cached": false,
      "cache_key": "c_1001:n_502:v3",
      "expires_at": "2026-03-20T10:00:00Z",
      "error_code": null,
      "error_message": null
    }
  }
  ```

* **错误示例 (404 Not Found)**：
  
  ```json
  {
    "code": "PREVIEW_TASK_NOT_FOUND",
    "message": "预览任务不存在或已过期",
    "request_id": "req_20260320_023",
    "details": {}
  }
  ```

> `status` 取值：`processing` | `completed` | `failed` | `cancelled`；`progress` 要求单调递增。

### 2.4 兼容接口：启动会话 / 生成预览（Deprecated）

**POST /sessions/start**  

* 通过 `mode: "learn" | "preview"` 分流到上述两个接口，返回体与 2.1 / 2.2 对齐。  
* 新代码应优先使用：`POST /learning-sessions` 与 `POST /preview-tasks`。  

---

## 3. 树形知识图谱检索 (Knowledge Graph RAG)

### 3.1 基于节点的知识检索

**POST /knowledge/retrieve**

* **描述**：根据用户问题及当前所在知识点，检索最相关的知识节点，用于 RAG 检索阶段。  

* **请求体**：
  
  ```json
  {
    "query": "什么是反向传播？",
    "current_node_id": "n_502",
    "path_node_ids": ["chap_1", "sec_3", "n_502"],
    "top_k": 3
  }
  ```

* **响应 (200 OK)**：
  
  ```json
  {
    "code": "OK",
    "message": "检索成功",
    "request_id": "req_20260320_030",
    "data": {
      "results": [
        {
          "node_id": "n_305",
          "content": "反向传播算法是...",
          "path": "/第一章/第三节/反向传播",
          "relevance_score": 0.92,
          "context": {
            "parent": "神经网络优化",
            "siblings": ["梯度下降", "学习率"]
          }
        }
      ]
    }
  }
  ```

> 如必须兼容字符串路径，可额外提供 `current_path` 字段，但建议标注为 Deprecated，并以 `current_node_id` 为主。

### 3.2 基于检索结果的答案生成

**POST /knowledge/answer**

* **描述**：在 3.1 的检索基础上，调用大模型生成面向学生/教师的自然语言答案。  

* **请求体**：
  
  ```json
  {
    "query": "什么是反向传播？",
    "current_node_id": "n_502",
    "top_k": 3,
    "audience": "student"
  }
  ```

* **响应 (200 OK)**：
  
  ```json
  {
    "code": "OK",
    "message": "生成成功",
    "request_id": "req_20260320_031",
    "data": {
      "answer": "反向传播是一种......",
      "used_nodes": [
        { "node_id": "n_305", "relevance_score": 0.92 },
        { "node_id": "n_310", "relevance_score": 0.85 }
      ]
    }
  }
  ```

---

## 4. 课程结构管理 (Course Structure)

### 4.1 获取课程树形大纲

**GET /courses/{course_id}/tree**

* **描述**：获取完整的课程树形结构。  

* **响应 (200 OK)**：
  
  ```json
  {
    "code": "OK",
    "message": "查询成功",
    "request_id": "req_20260320_040",
    "data": {
      "course_id": "c_1001",
      "root": {
        "id": "root_1",
        "title": "深度学习导论",
        "children": [
          {
            "id": "chap_1",
            "title": "第一章：基础知识",
            "children": []
          }
        ]
      }
    }
  }
  ```

### 4.2 课程节点 CRUD（教师端示例）

仅给出部分典型接口，其它可类推：  

* **创建节点**：`POST /courses/{course_id}/nodes`  
* **更新节点**：`PUT /courses/{course_id}/nodes/{node_id}`  
* **删除节点**：`DELETE /courses/{course_id}/nodes/{node_id}`  

请求体通常包括：`title`, `parent_id`, `order`, `metadata` 等；响应统一使用 0.1 的包裹结构。  

---

## 5. 学习进度与会话管理

### 5.1 上报学习进度

**POST /learning-sessions/{session_id}/progress**

* **描述**：学生端在学习过程中定期上报进度。  

* **请求体**：
  
  ```json
  {
    "current_node_id": "n_510",
    "progress": 0.35,
    "spent_seconds": 600
  }
  ```

### 5.2 查询学习进度

**GET /learning-sessions/{session_id}/progress**

* **描述**：查询指定会话的进度状态，用于续学、统计等。  

---

## 6. 预览管理

### 6.1 列出课程预览视频

**GET /courses/{course_id}/previews**

* **描述**：列出某课程下已有的视频预览及其缓存状态。  

### 6.2 删除预览 / 重新生成

**DELETE /previews/{preview_id}**

* **描述**：删除指定预览资源（同时清理缓存），供教师端管理。  

---

## 7. 列表、分页与幂等约定

* **分页**：统一使用 `page`（从 1 开始）与 `page_size`（默认 20，最大 100），响应中包含：`total`, `page`, `page_size`。  
* **排序**：列表接口如需排序，统一使用 `sort_by` 与 `order`（`asc` | `desc`）。  
* **幂等**：对可能被重复提交的异步任务（如预览生成），推荐支持 `Idempotency-Key` 请求头，服务端以 `(Idempotency-Key, user_id)` 作为幂等键，避免重复提交。  

---

## 8. 总体调用流程图

下图展示了前端与各后端模块之间的典型调用关系（Mermaid 语法，可在支持的 Markdown 工具中直接渲染）：

```mermaid
flowchart LR
    subgraph Client[前端客户端]
        UI[课程/学习界面]
    end

    subgraph Auth[鉴权服务]
        A1[POST /auth/login]
        A2[POST /auth/refresh]
        A3[POST /auth/logout]
    end

    subgraph Course[课程结构服务]
        C1[GET /courses/{course_id}/tree]
        C2[课程节点 CRUD\nPOST/PUT/DELETE /courses/{course_id}/nodes]
    end

    subgraph Learning[学习会话与进度服务]
        L1[POST /learning-sessions]
        L2[POST /learning-sessions/{session_id}/progress]
        L3[GET /learning-sessions/{session_id}/progress]
    end

    subgraph Preview[预览任务与管理服务]
        P1[POST /preview-tasks]
        P2[GET /preview-tasks/{preview_task_id}]
        P3[GET /courses/{course_id}/previews]
        P4[DELETE /previews/{preview_id}]
    end

    subgraph RAG[知识检索与答案生成服务]
        K1[POST /knowledge/retrieve]
        K2[POST /knowledge/answer]
    end

    %% 登录与鉴权
    UI -->|登录/退出| A1
    UI -->|刷新 token| A2
    UI -->|退出| A3

    %% 课程结构
    UI -->|加载课程大纲| C1
    UI -->|教师编辑大纲| C2

    %% 学习会话与进度
    UI -->|开始学习/续学| L1
    UI -->|上报进度| L2
    UI -->|查询进度| L3

    %% 预览任务
    UI -->|教师发起预览| P1
    UI -->|轮询预览状态| P2
    UI -->|查看预览列表| P3
    UI -->|删除/重生成预览| P4

    %% RAG
    UI -->|带当前 node 提问| K1
    K1 -->|检索结果| UI
    UI -->|请求答案生成| K2
    K2 -->|生成答案+引用节点| UI
```

# API 接口文档 v1.1

## 文档说明
本文档描述了基于树形知识图谱的在线教育辅助系统的后端接口。
*   **版本**：v1.1 (新增视频预览、鉴权模块)
*   **基础路径**：`/api/v1`
*   **鉴权方式**：Bearer Token (JWT)

---

## 1. 鉴权模块 (Authentication)

所有受保护接口需在 Header 中携带 `Authorization: Bearer <token>`。

### 1.1 获取访问令牌
**POST /auth/login**

*   **请求体**：
    ```json
    {
      "username": "teacher_01",
      "password": "password123"
    }
    ```
*   **响应 (200 OK)**：
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIs...",
      "token_type": "bearer",
      "expires_in": 3600,
      "user_role": "teacher" // or "student"
    }
    ```

---

## 2. 课程会话与视频预览 (Sessions & Preview)

### 2.1 启动学习会话 / 生成预览
**POST /sessions/start**

*   **描述**：
    *   **学生模式**：启动一次学习会话，记录学习进度。
    *   **教师模式 (新增)**：触发基于当前课件内容的视频预览生成任务。
*   **请求头**：`Authorization: Bearer <token>`
*   **请求体**：
    ```json
    {
      "course_id": "c_1001",
      "mode": "preview", // 必填: "learn" (学生) | "preview" (教师)
      "target_node_id": "n_502" // 可选: 指定从哪个知识点开始预览/学习
    }
    ```
*   **响应 (202 Accepted - 预览模式)**：
    ```json
    {
      "session_id": "sess_preview_8821",
      "task_id": "task_gen_preview_992", // 用于查询生成状态
      "message": "视频预览生成任务已提交"
    }
    ```
*   **响应 (201 Created - 学习模式)**：
    ```json
    {
      "session_id": "sess_learn_7731",
      "start_node": { ... }
    }
    ```

### 2.2 查询视频预览生成状态 (新增)
**GET /sessions/{session_id}/preview-status**

*   **描述**：查询异步生成的视频预览任务状态。支持缓存策略（若内容未变，直接返回缓存结果）。
*   **请求头**：`Authorization: Bearer <token>`
*   **响应 (200 OK - 生成中)**：
    ```json
    {
      "status": "processing",
      "progress": 45, // 百分比
      "eta_seconds": 15
    }
    ```
*   **响应 (200 OK - 完成)**：
    ```json
    {
      "status": "completed",
      "video_url": "https://cdn.example.com/previews/c_1001_n_502.mp4",
      "cached": true, // 标识是否命中缓存
      "expires_at": "2024-03-20T10:00:00Z"
    }
    ```
*   **响应 (404 Not Found)**：任务不存在或已过期。

---

## 3. 树形知识图谱检索 (Knowledge Graph RAG)

### 3.1 基于路径的知识检索
**POST /knowledge/retrieve**

*   **描述**：根据用户问题及当前学习路径，检索最相关的知识点。
*   **请求体**：
    ```json
    {
      "query": "什么是反向传播？",
      "current_path": "/第一章/第三节/神经网络基础", // 路径上下文
      "top_k": 3
    }
    ```
*   **响应 (200 OK)**：
    ```json
    {
      "results": [
        {
          "node_id": "n_305",
          "content": "反向传播算法是...",
          "path": "/第一章/第三节/反向传播",
          "relevance_score": 0.92,
          "context": {
            "parent": "神经网络优化",
            "siblings": ["梯度下降", "学习率"]
          }
        }
      ]
    }
    ```

---

## 4. 课程结构管理 (Course Structure)

### 4.1 获取课程树形大纲
**GET /courses/{course_id}/tree**

*   **描述**：获取完整的课程树形结构。
*   **响应 (200 OK)**：
    ```json
    {
      "course_id": "c_1001",
      "root": {
        "id": "root_1",
        "title": "深度学习导论",
        "children": [
          {
            "id": "chap_1",
            "title": "第一章：基础知识",
            "children": [...]
          }
        ]
      }
    }
    ```
