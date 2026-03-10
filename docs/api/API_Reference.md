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
(保持原有内容不变...)

### 3.3 学习会话 (Learning Sessions)
(保持原有内容不变...)

### 3.4 系统与配置 (System & Config)
(保持原有内容不变...)

### 3.5 数学流式计算 (Math Streaming Calculation)
(保持原有内容不变...)

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
- **UI 布局**: 建议采用双层布局。上层为“最终答案区”，下层为可折叠的“思考过程区”。
- **流式更新**:
  - 收到 `quick_answer` 时，更新“最终答案区”。
  - 收到 `enhanced_answer` 第一帧时，**清空**“最终答案区”的 Quick Answer 内容，开始重新渲染 Enhanced Answer。
  - 收到 `reasoning_content` 时，追加到“思考过程区”。

## 4. MCP 服务调用与前端展示规范
(保持原有内容不变...)

## 5. 数据字段总表 (Frontend Implementation Guide)

### 5.1 WebSocket 事件字段

| 事件名 (`type`) | 关键字段 (`content`/`data`) | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `token` | `content` | String | Yes | 答案生成的文本片段 |
| `sources` | `content` | List[SourceNode] | No | 引用来源列表 (含 bbox/image) |
| `strategy` | `content` | StrategyLog | No | **[新增]** AI 策略切换日志 |
| `resume` | `data` | ResumeData | No | **[新增]** 视频断点续接指令 |
| `quick_answer` | `content` | String | No | **[新增]** 双流模式下的快速响应 |
| `reasoning_content` | `content` | String | No | **[新增]** 深度思考过程 |

### 5.2 引用源对象 (SourceNode)

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `node_id` | String | Yes | 知识节点 ID |
| `content` | String | Yes | 文本摘要 |
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
