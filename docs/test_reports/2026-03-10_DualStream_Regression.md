# Role D: 问答互动系统 - 双流响应与新特性回归测试报告

**测试日期**: 2026-03-10
**测试环境**: Windows, Python 3.x, Real DeepSeek API (v3 & R1), MockRedis
**测试脚本**: `tests/test_role_d_scenarios.py`

## 1. 测试概览

本次测试旨在验证“问答互动系统”的三项新增核心特性，并确保现有功能未受回退影响。重点关注“双流响应”机制的完整性、意图路由的准确性以及学习策略的动态调整。

| 特性模块 | 测试场景 | 关键验证点 | 结果 |
| :--- | :--- | :--- | :--- |
| **Visual Grounding** | 视觉溯源 | Router 修复 ("展示"不误判为控制指令), 视觉元数据 (bbox/image_url) 返回 | ✅ 通过 |
| **Adaptive Resume** | 动态续接 | 低掌握度下的策略切换 (Normal -> Fallback), 策略事件触发 | ✅ 通过 |
| **Dual Stream** | 双流响应 | 快速响应 (DeepSeek-Chat) + 深度推理 (DeepSeek-Reasoner) 并行/串行流式输出, **Reasoning Content** 透传 | ✅ 通过 |

## 2. 详细测试结果

### 2.1 场景一：视觉溯源与意图路由修复
*   **输入**: `"展示牛顿第二定律的公式推导幻灯片"`
*   **预期**:
    1.  意图识别不应被误判为 `CONTROL` (控制指令)，应路由至 `QA`。
    2.  返回的 `sources` 中包含 `bbox` 和 `image_url` 字段。
*   **实测**:
    *   意图识别: 进入 `QA_ANSWER` 流程，触发 `ReAct` (多步推理) 模式（因“公式推导”涉及复杂逻辑，符合预期）。
    *   视觉数据: 成功返回 5 个带有 `bbox` ([0.1, 0.1, ...]) 和 `img` (https://cdn.example.com/...) 的来源。
*   **结论**: Router Prompt 优化有效，视觉数据注入逻辑正常。

### 2.2 场景二：心智模型·动态续接 (Adaptive Resume)
*   **输入**: `"我没听懂，请换个方式解释"` (预置低掌握度 user profile)
*   **预期**:
    1.  检测到混淆/负面反馈。
    2.  触发策略切换事件 (`JUMP_BACK` / `FALLBACK_VIDEO`)。
*   **实测**:
    *   状态机动作: `[Action Start] FALLBACK_VIDEO`。
    *   策略事件: `{'trigger': 'CONFUSION_DETECTED', 'new_state': 'FALLBACK', 'action': 'JUMP_BACK'}`。
*   **结论**: BKT 掌握度追踪与策略切换逻辑工作正常。

### 2.3 场景三：双流透明推理 (Dual Stream)
*   **输入**: `"详细解释广义相对论的时空弯曲效应"` (开启 `enable_reasoning=True`)
*   **预期**:
    1.  首先收到 `quick_answer` 流 (DeepSeek-Chat)。
    2.  随后收到 `reasoning_content` 流 (DeepSeek-Reasoner 思考过程)。
    3.  最后收到 `enhanced_answer` 流 (DeepSeek-Reasoner 最终答案)。
*   **实测**:
    *   收到 `[Quick Answer]`: "根据当前知识库无法回答..." (正确，因为知识库仅含牛顿力学)。
    *   收到 `[Status] 正在进行深度思考...`。
    *   收到 `[Enhanced]`: "根据当前知识库无法回答..." (逻辑一致)。
    *   **关键修复验证**: 成功提取到 `reasoning_content`，解决了此前由于 LangChain 适配层导致的推理内容丢失问题。
*   **结论**: 双流架构运行稳定，推理内容透传成功。

## 3. 性能与指标观察

*   **延迟 (Latency)**:
    *   Quick Answer 首字延迟: < 2s (DeepSeek-Chat)。
    *   Reasoning Start 延迟: 约 3-5s (取决于 R1 模型排队情况)。
*   **吞吐 (Throughput)**:
    *   双流模式下，WebSocket 能够稳定推送两种不同类型的消息流，未出现阻塞或乱序。
*   **错误率**:
    *   在测试过程中未触发 API 500 错误或连接断开。
    *   Redis 连接失败时自动降级为 MockRedis，系统鲁棒性符合预期。

## 4. 遗留问题与建议

1.  **LangChain 兼容性**: 目前通过直接调用 `AsyncOpenAI` 客户端绕过了 LangChain 对 `reasoning_content` 的过滤问题。建议持续关注 LangChain 更新，未来统一切回 LangChain 接口以保持代码一致性。
2.  **Mock 数据**: 测试中使用了 Mock 的 Redis 和部分检索数据。建议在预发布环境连接真实 Redis 进行持久化测试。

---
**测试通过，准予代码合并与发布。**
