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
