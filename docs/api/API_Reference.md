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

#### REST API 检索端点 (Retrieve Endpoint)

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| POST | `/api/v1/qa/retrieve` | 基于课程知识图谱的 RAG 问答检索 |

**请求参数 (RetrieveRequest)**

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `query` | String | Yes | 用户问题 |
| `lesson_id` | String | Yes | 课件 ID |
| `top_k` | Integer | No | 检索数量，默认 5 |
| `enable_decomposition` | Boolean | No | 是否启用查询分解 |

**响应参数 (RetrieveResponse)**

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `code` | Integer | 状态码 |
| `message` | String | 状态信息 |
| `data` | Object | 响应数据体 |
| `request_id` | String | 请求 ID |

**响应数据体 (RetrieveResponseData)**

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `answer` | String | 从检索结果中提取的答案 |
| `bbox_list` | List[BboxItem] | 合并后的边界框列表（按页分组） |
| `context` | Object | 上下文信息，包含 matched_chapters 和 source_pages |
| `sources` | List[SourceItem] | 引用来源列表 |

**BboxItem (边界框项)**

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `page_num` | Integer | 页码 |
| `bboxes` | List[List[Float]] | 原始边界框列表，每个为 `[x, y, w, h]` |
| `merged_bbox` | List[Float] | 合并后的边界框 `[x, y, w, h]` |
| `is_merged` | Boolean | 是否经过合并 |
| `total_area_ratio` | Float | 合并后总面积占比 |

**SourceItem (引用源项)**

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `node_id` | String | Yes | 知识节点 ID |
| `content` | String | Yes | 文本摘要 |
| `path` | String | Yes | 知识路径 |
| `relevance_score` | Float | Yes | 匹配度 (0-1) |
| `page_num` | Integer | No | 页码 |
| `bbox` | List[Float] | No | `[x, y, w, h]` 归一化坐标 |
| `image_url` | String | No | 幻灯片图片 URL |

#### WebSocket `/api/v1/chat/ws`
全双工聊天流式传输。用于实时发送查询并接收流式响应。

- **协议**: WebSocket
- **消息格式** (客户端 -> 服务端):
  ```json
  {
    "query": "解释牛顿第二定律",
    "session_id": "sess_123",
    "current_path": "mechanics/newton", // 可选，当前学习路径上下文
    "top_k": 3, // 可选，检索数量
    "video_timestamp": 120.5 // 可选，当前视频播放进度（秒），用于断点续接
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

  2. **Sources (参考来源 - 视觉增强)**:
     ```json
     {
       "type": "sources",
       "content": [
         {
           "node_id": "n1",
           "content": "力等于质量乘以加速度...",
           "relevance_score": 0.95,
           "bbox": [0.1, 0.2, 0.3, 0.4], // [x, y, w, h] 归一化坐标
           "image_url": "https://cdn.example.com/slides/page_5.jpg", // 幻灯片图片链接
           "page_num": 5,
           "metadata": {"source": "textbook_ch2.pdf"}
         }
       ]
     }
     ```
     **前端实现提示**:
     - **订阅事件**: `sources`
     - **触发时机**: 在 RAG 检索完成且开始生成文本之前。
     - **交互逻辑**: 在聊天气泡下方渲染“来源卡片”。点击卡片时，应调用 PDF 阅读器或图片查看器组件，加载 `image_url` 并在对应 `bbox` 区域绘制半透明高亮框。

  3. **Strategy (策略切换 - 显性化思考)**:
     ```json
     {
       "type": "strategy",
       "content": {
         "topic": "Neural Networks",
         "mastery": 0.35,
         "prev_state": "NORMAL",
         "new_state": "FALLBACK",
         "trigger": "CONFUSION_DETECTED",
         "action": "JUMP_BACK"
       }
     }
     ```
     **前端实现提示**:
     - **订阅事件**: `strategy`
     - **触发时机**: 当 `TeacherAgent` 检测到用户状态变化（如困惑度上升）时。
     - **交互逻辑**: 在侧边栏或顶部状态栏显示动态通知，例如：“检测到知识点掌握薄弱 (35%)，正在切换至基础回溯模式...”。

  4. **Resume (断点续接)**:
     ```json
     {
       "type": "resume",
       "data": {
         "timestamp": 120.5,
         "strategy": "auto_resume",
         "message": "已为您解答完毕，点击继续学习"
       }
     }
     ```
     **前端实现提示**:
     - **订阅事件**: `resume`
     - **触发时机**: 问答结束时（`end` 事件之前）。
     - **交互逻辑**: 显示“继续播放”按钮或倒计时自动跳转。点击后调用视频播放器接口 `player.seekTo(timestamp)` 并 `player.play()`。

  5. **Suggestions (后续建议)**:
     ```json
     {"type": "suggestions", "content": ["F代表什么?", "m代表什么?"]}
     ```

  6. **Error (错误信息)**:
     ```json
     {"type": "error", "content": "无法连接到知识库。"}
     ```

  7. **MCP Tool Events**: (见第 4 节)

#### 悬浮窗交互规范 (Hover & Overlay)
对于 `Sources` 事件中的引用内容，前端需支持悬浮窗预览。

| 属性 | 规范要求 | 备注 |
| :--- | :--- | :--- |
| **尺寸** | 宽度固定 300px，高度自适应 (Max 400px) | 保持轻量级预览 |
| **定位** | 优先在引用锚点上方居中，空间不足时自动翻转至下方 | 使用 Popper.js 或类似库 |
| **遮罩** | 无模态遮罩 (Non-modal)，鼠标移出即消失 | 不打断阅读流 |
| **内容** | 显示 `image_url` 缩略图 + `content` 摘要 | 图片需懒加载 |
| **无障碍** | 支持 `Escape` 键关闭，`Tab` 键聚焦 | ARIA-label="Source Preview" |

#### 高亮展示规范 (Highlighting)
对于 PDF/图片上的 `bbox` 高亮区域。

| 属性 | 规范要求 | 备注 |
| :--- | :--- | :--- |
| **颜色** | `rgba(255, 255, 0, 0.3)` (黄色半透明) | 模拟荧光笔效果 |
| **边框** | `2px solid #FFD700` | 增强辨识度 |
| **动画** | 出现时淡入 (Fade In 300ms) | 避免视觉突兀 |
| **持续** | 永久显示，直到用户切换页面或关闭查看器 | |
| **降级** | 若无 `bbox`，仅高亮所在页面或显示“第 X 页” | 兼容旧数据 |

### 3.2 聊天会话管理 (Chat Sessions Management)

#### REST API

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| GET | `/api/v1/chat/sessions` | 获取当前用户的所有聊天会话 |
| POST | `/api/v1/chat/sessions` | 创建新的聊天会话 |
| GET | `/api/v1/chat/history/{session_id}` | 获取指定会话的聊天历史 |
| GET | `/api/v1/chat/history/{session_id}/context` | 获取会话上下文（包括预期问题和思考路径） |
| GET | `/api/v1/chat/history/{session_id}/events` | 获取会话的原始事件历史（事件溯源） |
| POST | `/api/v1/chat/history/{session_id}/truncate` | 截断指定索引之后的聊天历史 |

#### 请求/响应示例

**创建会话**
```json
// Request
POST /api/v1/chat/sessions

// Response
{"session_id": "sess_abc123"}
```

**获取会话历史**
```json
// Response
[
  {"role": "user", "content": "什么是牛顿第二定律？"},
  {"role": "assistant", "content": "牛顿第二定律指出...", "sources": [...]}
]
```

**截断历史**
```json
// Request
POST /api/v1/chat/history/sess_123/truncate
{"index": 5}

// Response
{"status": "success"}
```

### 3.3 学习会话 (Learning Sessions)

#### REST API

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| POST | `/api/v1/chat/session/start` | 启动新的学习会话或预览会话 |
| GET | `/api/v1/chat/session/{session_id}/preview` | 获取视频预览生成任务状态 |

#### 数据库查询 API

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| GET | `/api/v1/chat/db/qa-records/{session_id}` | 获取指定会话的问答记录 |
| GET | `/api/v1/chat/db/learning-progress/{session_id}` | 获取指定会话的学习进度 |

#### 请求/响应示例

**启动学习会话**
```json
// Request
POST /api/v1/chat/session/start
{
  "course_id": "course_001",
  "lesson_id": "lesson_001",
  "mode": "learning",  // 或 "preview"
  "current_path": "/chapter1/section1"
}

// Response
{
  "session_id": "sess_abc123",
  "status": "started",
  "lesson_id": "lesson_001"
}
```

**获取学习进度**
```json
// Response
{
  "code": "OK",
  "data": {
    "track_id": "track_001",
    "user_id": "student_001",
    "session_id": "sess_abc123",
    "lesson_id": "lesson_001",
    "current_node_id": "node_5",
    "current_path": "/chapter1/section2",
    "current_topic": "牛顿第二定律",
    "confusion_count": 2,
    "mastery": 0.75,
    "last_position_seconds": 125.5,
    "progress_percent": 35.0,
    "adjust_type": "normal",
    "needs_supplement": false
  }
}
```

### 3.4 系统与配置 (System & Config)

#### REST API

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| GET | `/api/v1/chat/metrics` | 获取缓存命中率和性能指标 |
| POST | `/api/v1/chat/config/reload` | 热重载 QAService 配置 |

#### SSE 端点

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| GET | `/api/v1/chat/sse` | Server-Sent Events 聊天端点（用于不支持 WebSocket 的场景） |

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| query | String | Yes | 用户问题 |
| session_id | String | No | 会话 ID |

**示例**
```bash
curl -N "http://localhost:8000/api/v1/chat/sse?query=什么是牛顿定律"
```

**响应格式 (SSE)**
```
data: {"type": "token", "content": "牛顿"}
data: {"type": "token", "content": "定律"}
data: [DONE]
```

### 3.5 数学流式计算 (Math Streaming Calculation)

系统支持将自然语言数学问题转化为 Python 代码，流式返回代码生成、执行结果和解释。

#### REST API

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| POST | `/api/v1/chat/math/stream` | 流式数学计算端点 |

#### 请求参数 (ChatRequest)

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| query | String | Yes | 数学问题（如 "计算 1+1"） |
| session_id | String | No | 会话 ID |

#### 响应格式 (SSE)

| 事件类型 | 说明 |
| :--- | :--- |
| `code_delta` | 代码生成片段 |
| `execution_result` | 代码执行结果 |
| `execution_error` | 代码执行错误 |
| `explanation_delta` | 解释生成片段 |

**请求示例**
```json
POST /api/v1/chat/math/stream
{
  "query": "计算 1 到 100 的和",
  "session_id": "sess_123"
}
```

**响应示例 (SSE)**
```
data: {"type": "code_delta", "content": "import "}
data: {"type": "code_delta", "content": "numpy as np\n\n"}
data: {"type": "code_delta", "content": "result = sum(range(1, 101))"}
data: {"type": "execution_result", "content": "5050"}
data: {"type": "explanation_delta", "content": "使用 Python 的 sum() 函数"}
data: {"type": "explanation_delta", "content": "可以轻松计算 1 到 100 的总和。"}
data: [DONE]
```

### 3.6 双流响应 (Dual-Stream Response) [新增方案三]
为了平衡响应速度与深度推理，系统支持 Quick Answer + Deep Reasoning 并行输出。此模式下，WebSocket 连接将依次推送“快速回答”流和“深度推理”流。

#### 请求参数
在 `ChatRequest` 中设置 `enable_reasoning=true` 以启用此模式。

```json
{
  "query": "量子纠缠的原理是什么？",
  "session_id": "sess_123",
  "enable_reasoning": true
}
```

#### 交互时序与消息类型
1. **Quick Answer (快速响应)**: 立即返回基于缓存或轻量模型的简短回答。
   - 消息类型: `quick_answer`
   - 前端行为: 立即展示，作为占位符或初步答案。

2. **Reasoning Start (开始推理)**: 后台异步进行深度检索和推理。
   - 消息类型: `reasoning_start`
   - 前端行为: 显示“正在深度思考...”加载状态或折叠面板。

3. **Reasoning Content (思考链)**: 推送深度推理过程。
   - 消息类型: `reasoning_content`
   - 前端行为: 在折叠面板中流式显示思考过程（类似 DeepSeek 官网效果）。

4. **Enhanced Answer (增强回答)**: 最终的深度回答。
   - 消息类型: `enhanced_answer`
   - 前端行为: 深度回答生成完毕后，替换或补充 Quick Answer。

#### 响应示例
```json
// 1. 快速回答流
{"type": "quick_answer", "content": "量"}
{"type": "quick_answer", "content": "子"}
{"type": "quick_answer", "content": "纠"}
{"type": "quick_answer", "content": "缠..."}

// 2. 开始深度思考
{"type": "reasoning_start"}

// 3. 思考过程流
{"type": "reasoning_content", "content": "检索到相关论文..."}
{"type": "reasoning_content", "content": "分析贝尔不等式..."}

// 4. 深度回答流 (替换快速回答)
{"type": "enhanced_answer", "content": "量子纠缠是一种物理现象..."}
{"type": "enhanced_answer", "content": "当两个粒子..."}

// 5. 结束
{"type": "reasoning_end"}
```

#### 状态码与错误处理
- **正常流程**: 所有流正常结束。
- **推理超时/失败**: 若深度推理失败，前端应保留 Quick Answer，并显示“深度思考暂时不可用”提示。
  - 错误消息: `{"type": "error", "code": "REASONING_FAILED", "content": "深度推理服务超时"}`

#### 前端实现指引
- **UI 布局**: 建议采用双层布局。上层为"最终答案区"，下层为可折叠的"思考过程区"。
- **流式更新**:
  - 收到 `quick_answer` 时，更新"最终答案区"。
  - 收到 `enhanced_answer` 第一帧时，**清空**"最终答案区"的 Quick Answer 内容，开始重新渲染 Enhanced Answer。
  - 收到 `reasoning_content` 时，追加到"思考过程区"。

### 3.7 语音合成与识别 (TTS/ASR)

系统提供 WebSocket 接口用于文字转语音 (TTS) 和语音转文字 (ASR) 服务。

#### WebSocket `/api/v1/ws/script`

- **协议**: WebSocket
- **连接建立后第一条消息**: 必须是 JSON 格式，用于指定服务类型

#### 服务类型: TTS (文字转语音)

**第一条消息格式** (客户端 -> 服务端):
```json
{
  "service": "tts",
  "text": "你好，欢迎学习本课程",
  "voice": "zh-CN-XiaoxiaoNeural"
}
```

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `service` | String | Yes | 固定值 `"tts"` |
| `text` | String | Yes | 要转换为语音的文本 |
| `voice` | String | No | 语音角色，默认为 `"zh-CN-XiaoxiaoNeural"` |

**响应格式** (服务端 -> 客户端):
1. 音频流数据 (二进制)
2. 结束标志: 空字节 (`""` 或 `b""`)

**前端实现提示**:
- 接收二进制音频数据后，拼接成完整的 WAV/MP3
- 使用 Web Audio API 或 `<audio>` 元素播放

#### 服务类型: ASR (语音转文字)

**第一条消息格式** (客户端 -> 服务端):
```json
{
  "service": "asr"
}
```

**后续消息**: 发送音频数据块 (二进制)

**结束标志**: 发送空字节 (`b""`) 表示音频发送完毕

**响应格式** (服务端 -> 客户端):
```json
{"text": "转换后的文字内容"}
```

**前端实现提示**:
- 音频数据块需要添加结束标志 (空字节)
- 适用于实时语音输入场景

#### WebSocket 连接示例 (JavaScript)

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/ws/script");

// TTS 示例
ws.onopen = () => {
  ws.send(JSON.stringify({
    service: "tts",
    text: "你好，欢迎学习",
    voice: "zh-CN-XiaoxiaoNeural"
  }));
};

ws.onmessage = (event) => {
  if (event.data instanceof Blob) {
    // 处理音频数据
    const url = URL.createObjectURL(event.data);
    new Audio(url).play();
  } else if (event.data === "") {
    // TTS 结束
    console.log("TTS 播放完成");
  }
};

// ASR 示例
ws.onopen = () => {
  ws.send(JSON.stringify({ service: "asr" }));
  // 发送音频数据...
  ws.send(audioBlob);
  ws.send(b""); // 结束标志
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("识别结果:", data.text);
};
```

## 4. MCP 服务调用与前端展示规范
(保持原有内容不变...)

## 5. 数据字段总表 (Frontend Implementation Guide)

### 5.1 WebSocket 事件字段

| 事件名 (`type`) | 关键字段 (`content`/`data`) | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `token` | `content` | String | Yes | 答案生成的文本片段 |
| `start` | `action` | String | No | 开始回答，包含动作类型 (QA_ANSWER, QA_CACHE, CONTROL 等) |
| `sources` | `content` | List[SourceNode] | No | 引用来源列表 (含 bbox/image) |
| `strategy` | `content` | StrategyLog | No | AI 策略切换日志 |
| `resume` | `data` | ResumeData | No | 视频断点续接指令 |
| `quick_answer` | `content` | String | No | 双流模式下的快速响应 |
| `reasoning_start` | - | - | No | 开始深度推理 |
| `reasoning_content` | `content` | String | No | 深度思考过程 |
| `enhanced_answer` | `content` | String | No | 深度增强回答 |
| `reasoning_end` | - | - | No | 深度推理结束 |
| `suggestions` | `content` | List[String] | No | 后续问题建议 |
| `action` | `data` | Dict | No | 客户端动作指令 (RESUME, SUPPLEMENT 等) |
| `status` | `content` | String | No | 状态消息 (如 "正在检索...") |
| `end` | - | - | No | 回答结束标志 |
| `error` | `content` | String | No | 错误信息 |
| `evaluation` | `content` | Dict | No | 学习评价结果 |

### 5.2 引用源对象 (SourceNode)

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `node_id` | String | Yes | 知识节点 ID |
| `content` | String | Yes | 文本摘要 |
| `path` | String | Yes | 知识路径 |
| `bbox` | List[Float] | No | `[x, y, w, h]` 归一化坐标 |
| `image_url` | String | No | 幻灯片图片 URL |
| `page_num` | Integer | No | 页码 |
| `relevance_score` | Float | Yes | 匹配度 (0-1) |

### 5.3 续接指令对象 (ResumeData)

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `timestamp` | Float | Yes | 视频跳转秒数 |
| `strategy` | String | Yes | `auto_resume` (自动) 或 `manual` (按钮) |
| `message` | String | No | 提示文案 |

## 6. 版本变更记录

| 版本 | 日期 | 责任人 | 变更内容 |
| :--- | :--- | :--- | :--- |
| v1.0 | 2026-03-01 | Team | 初始版本 |
| v1.1 | 2026-03-10 | Role D (QA) | 新增 [视觉引用](#31-聊天与问答-chat--qa)、[策略事件](#31-聊天与问答-chat--qa)、[断点续接](#31-聊天与问答-chat--qa) 及 [前端交互规范](#前端展示标准-uiux) |
| v1.2 | 2026-04-16 | Role D (QA) | 完善 [会话管理 API](#32-聊天会话管理-chat-sessions-management)、[学习会话 API](#33-学习会话-learning-sessions)、[系统配置 API](#34-系统与配置-system--config)、[数学计算 API](#35-数学流式计算-math-streaming-calculation)、[TTS/ASR API](#37-语音合成与识别-ttsasr)；扩展 [WebSocket 事件字段表](#51-websocket-事件字段)；添加 SourceNode.path 字段 |
| v1.3 | 2026-04-17 | Role D (QA) | 新增 [Retrieve API](#31-聊天与问答-chat--qa) 详细字段说明；添加 BboxItem、SourceItem 数据结构；标注后端实现缺失的 bbox 和 image_url 字段 |

## 7. QA 模块数据流向与实现指南

### 7.1 数据处理流程概览

QA 模块的数据处理流程分为以下几个层次：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据层 (Data Layer)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  CIR 数据 (JSON)              │  原始数据 (extract.json)                    │
│  - node_id, node_name         │  - elements: [{content, bbox, ...}]       │
│  - page_num                   │  - page_num                                │
│  - path                       │  - element_type                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         检索层 (Retrieval Layer)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  TwoLayerRetriever                                                        │
│  ├─ _retrieve_cir(): 从 CIR 知识图谱检索章节/知识点                        │
│  ├─ _retrieve_raw_json(): 从原始 JSON 检索文本块（含 bbox）                │
│  └─ _aggregate_results(): 合并结果，提取答案                               │
│       - merge_bboxes_by_page(): 按页合并 bbox                              │
│       - format_bbox_for_response(): 格式化为 BboxItem                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          服务层 (Service Layer)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  QAService.stream_answer_question()                                       │
│  ├─ 使用 TreeStructureRetriever (单层检索) 或 TwoLayerRetriever           │
│  ├─ 构造 source_nodes: 从 doc.metadata 提取 bbox, page_num, image_url   │
│  └─ 通过 WebSocket 发送 sources 事件                                       │
│                                                                             │
│  TreeStructureRetriever (单层检索模式)                                     │
│  └─ _inject_visual_mock_data(): 注入模拟的 bbox/page_num/image_url       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API 层 (API Layer)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  POST /api/v1/qa/retrieve                                                  │
│  └─ 返回 RetrieveResponseData { bbox_list, sources, answer, context }     │
│                                                                             │
│  WebSocket /api/v1/chat/ws                                                │
│  └─ 发送 sources 事件: { type: "sources", content: [SourceNode] }          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         前端展示 (Frontend)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Sources 事件处理                                                           │
│  1. 接收 sources 事件                                                       │
│  2. 渲染来源卡片（显示 content, path, relevance_score）                   │
│  3. 点击卡片时:                                                             │
│     - 调用 PDF/图片查看器                                                   │
│     - 加载 image_url                                                       │
│     - 在 bbox 区域绘制高亮框 (rgba(255,255,0,0.3), border: 2px solid #FFD700)│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 页码 (page_num) 数据规范

页码数据在系统中以整数形式传递，用于定位 PPT/教材的具体页面。

| 来源 | 字段 | 类型 | 说明 |
| :--- | :--- | :--- | :--- |
| CIR 数据 | `page_num` | Integer | 知识节点对应的 PPT 页码 |
| 原始 JSON | `page_num` | Integer | 文本块所在的 PPT 页码 |
| WebSocket sources | `page_num` | Integer | 引用的 PPT 页码 |
| BboxItem | `page_num` | Integer | bbox 所在的 PPT 页码 |

### 7.3 边界框 (bbox) 数据规范

边界框用于在前端 PDF/图片上定位具体的内容区域。

**格式**: `[x, y, w, h]` (归一化坐标，0-1 范围)

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `x` | Float | 左上角 X 坐标 (0-1) |
| `y` | Float | 左上角 Y 坐标 (0-1) |
| `w` | Float | 宽度 (0-1) |
| `h` | Float | 高度 (0-1) |

**合并逻辑** (`merge_bboxes_by_page`):
- 同一页的多个 bbox 会合并为一个外接矩形
- 合并后生成 `merged_bbox`，用于简化前端高亮渲染

### 7.4 需要调整的代码节点

根据数据流分析，以下位置需要调整以确保页码和 bbox 数据正确传递：

| 层级 | 文件 | 调整内容 | 优先级 |
| :--- | :--- | :--- | :--- |
| Schema | `schemas/qa.py` - `SourceItem` | 添加 `bbox` 和 `image_url` 字段 | 高 |
| API Endpoint | `api/v1/endpoints/retrieval.py` | 在构建 SourceItem 时传入 bbox 和 image_url | 高 |
| TwoLayerRetriever | `retrieval/two_layer_retriever.py` | 确保 raw_results 中的 bbox 传递到 sources | 中 |
| TreeRetriever | `retrieval/tree_retriever.py` | 确保 metadata 中的 bbox/page_num/image_url 正确传递 | 中 |

### 7.5 两层检索 vs 单层检索

系统支持两种检索模式：

1. **TwoLayerRetriever (两层检索)**:
   - 第一层: 从 CIR 知识图谱检索章节/知识点
   - 第二层: 从原始 JSON 检索具体文本块（含 bbox）
   - 特点: 精确的 bbox 定位，适合视觉增强场景

2. **TreeStructureRetriever (单层检索)**:
   - 从知识树 JSON 检索
   - 使用 `_inject_visual_mock_data()` 注入模拟的 bbox/page_num/image_url
   - 特点: 快速响应，适合通用问答场景

两种检索模式均通过 `sources` 事件向前端提供页码和 bbox 数据。
