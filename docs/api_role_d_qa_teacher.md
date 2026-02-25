# Role D: QA & Teacher Agent API 接口文档

## 1. 概述
本模块负责处理学生与系统的所有实时交互，包括：
- **智能问答 (QA)**: 基于树形知识图谱的 RAG 检索。
- **情感反馈 (Feedback)**: 识别学生困惑并在必要时触发补讲。
- **进度控制 (Control)**: 处理“继续”、“暂停”等指令。
- **状态管理**: 实时追踪学生画像和困惑度。

## 2. 接口列表

### 2.1 核心对话接口

**POST** `/api/v1/chat/chat`

用于发送学生的问题、反馈或指令。系统会自动路由并返回相应动作。

**请求参数 (JSON Body)**:

```json
{
  "query": "老师，我不懂为什么力是改变物体运动状态的原因？", // 用户输入
  "session_id": "sess_12345678", // 会话 ID (可选，若不传则视为无状态或Demo会话)
  "current_path": "physics/mechanics/newton_laws", // 当前 PPT/视频 所在的知识点路径
  "top_k": 3 // RAG 检索的文档数量 (默认 3)
}
```

**响应示例 (ChatResponse)**:

**情况 A: 正常问答 (QA)**
```json
{
  "answer": "力是改变物体运动状态的原因，因为根据牛顿第一定律...",
  "session_id": "sess_12345678",
  "action": "QA_ANSWER",
  "source_nodes": [ // 引用来源
    {
      "node_id": "node_101",
      "content": "牛顿第一定律指出...",
      "relevance_score": 0.85
    }
  ]
}
```

**情况 B: 触发补讲 (SUPPLEMENT)**
*当用户说“不懂”、“太难了”且困惑度累积时触发*
```json
{
  "answer": "看来这个概念确实比较抽象。我们可以这样想：想象你在推一辆超市购物车...", // 类比解释
  "session_id": "sess_12345678",
  "action": "SUPPLEMENT",
  "action_data": {
    "action": "SUPPLEMENT",
    "audio_text": "...", // 用于 TTS 的文本
    "content": "..."
  }
}
```

**情况 C: 兜底跳转 (FALLBACK_VIDEO)**
*当用户连续困惑多次时触发*
```json
{
  "answer": "我看这部分确实比较难，建议你直接观看详细视频讲解。",
  "session_id": "sess_12345678",
  "action": "FALLBACK_VIDEO",
  "action_data": {
    "video_jump_link": "/course/video/physics_intro?t=120"
  }
}
```

### 2.2 会话管理接口

**POST** `/api/v1/chat/session/start`

开始一个新的学习会话或视频生成任务。

**请求参数**:
```json
{
  "course_id": "course_001",
  "mode": "learning", // "learning" (实时学习) 或 "preview" (生成预习视频)
  "target_node_id": "node_start"
}
```

**响应**:
```json
{
  "session_id": "sess_abc123",
  "status": "active",
  "message": "Learning session started."
}
```

### 2.3 学生画像接口

**GET** `/api/v1/student/profile`
**POST** `/api/v1/student/profile`

获取或更新学生画像（如学习风格、薄弱点）。

**POST Body**:
```json
{
  "weaknesses": ["力学", "电磁感应"],
  "learning_style": "visual", // "visual", "auditory", "textual"
  "interaction_mode": "personalized" // "standard", "personalized"
}
```

### 2.4 手动重置困惑度 (Reset Confusion)
`POST /api/v1/chat/session/feedback/reset?session_id={id}`

用于前端在学生表示“听懂了”或点击相关按钮时，重置系统的困惑计数器。

**Response**:
```json
{
  "status": "success",
  "message": "Confusion count reset."
}
```

### 2.5 脚本风格迁移 (Script Adaptation)
`POST /api/v1/chat/script/adapt`

**用于演示亮点**：在学生与助教互动结束后，前端调用此接口将后续的课程脚本进行“风格迁移”（如根据学生偏好改为更通俗的语言），实现个性化教学。

**Request**:
```json
{
  "original_script": "牛顿第二定律表明，物体的加速度与所受合外力成正比...",
  "session_id": "sess_12345678",
  "target_style": "humorous" // 可选，不传则使用学生画像中的默认风格
}
```

**Response**:
```json
{
  "adapted_script": "咱们来聊聊牛顿第二定律，这其实就像你推超市购物车...",
  "style_applied": "visual",
  "processing_time": 1.23
}
```

## 3. 前端开发建议 (Frontend Guidelines)

1.  **快捷回复按钮**:
    为了提升演示流畅度，建议在聊天框上方常驻以下快捷按钮（点击即发送对应文本）：
    *   🔘 **"没听懂，再讲一遍"** (触发 Feedback -> Supplement)
    *   🔘 **"举个例子"** (触发 QA/Supplement)
    *   🔘 **"太难了"** (累积困惑度 -> 可能触发 Fallback)
    *   🔘 **"继续"** (触发 Control -> Resume)

2.  **状态反馈**:
    当 API 返回 `action: "SUPPLEMENT"` 时，前端应暂停主视频，播放返回的 `answer`（通过 TTS 接口或文本展示），并显示“AI 正在为您个性化补讲”的动效。

3.  **演示模式 (Demo Mode)**:
    在比赛演示时，建议先调用 `/api/v1/student/profile` 将 `learning_style` 设置为 `visual` 或 `auditory`，以展示不同风格的 AI 回复差异。
