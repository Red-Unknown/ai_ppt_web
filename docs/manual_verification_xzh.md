# 人工验证方案（xzh）

## 1. 验证范围
- 后端接口：WebSocket `/api/v1/chat/ws`、SSE `/api/v1/chat/sse`、`/api/v1/chat/metrics`、`/api/v1/chat/config/reload`
- 前端页面：Role D Playground（最小可用UI）：查询输入、会话信息、流式输出、来源说明、建议问题、指标查看、配置热加载
- 数据：fixtures/mock_xzh 冻结数据存在性与校验信息

## 2. 前置条件
- 已配置 DeepSeek KEY（可使用本地mock：`set DEEPSEEK_API_KEY=sk-mock-key`）
- 启动后端服务（需在项目根目录）：
  - Windows/Linux/Mac: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
- 冻结数据生成：`python scripts/data_freeze_xzh.py`（fixtures/README.md 已追加校验信息）

## 3. 验证步骤与预期

### 3.1 数据冻结
1. 执行 `python scripts/data_freeze_xzh.py`
2. 打开 `fixtures/mock_xzh` 目录，确认存在 `course_xzh.json`、`graph_xzh.json`、`retriever_docs_xzh.jsonl`
3. 打开 `fixtures/README.md`，确认新增一节 Freeze 记录，包含每个文件的 MD5 与行数

预期：所有文件存在且 MD5/行数记录完整，未覆盖历史记录

### 3.2 后端接口
1. WebSocket：使用前端或 Postman WS 连接 `/api/v1/chat/ws`，发送
   ```json
   {"query":"课程介绍","session_id":"sess_ui","current_path":"intro"}
   ```
   预期：按序收到 `start(QA_CACHE)` → `token`(文本) → `suggestions`(3条) → `end`
2. SSE：访问 `/api/v1/chat/sse?query=课程介绍&session_id=sess_ui&current_path=intro`
   预期：以 `data: {...}\n\n` 形式输出事件，最终包含 `end`
3. 指标：`GET /api/v1/chat/metrics` 返回命中率字段（hits/misses/total/hit_rate）
4. 热加载：`POST /api/v1/chat/config/reload` 返回 `{"status":"success"}`
5. 安全过滤：通过WS发送 `{"query":"rm -rf /","session_id":"s1","current_path":"x"}`
   预期：立即返回 `{"type":"error","content":"Edge Security: Malicious content detected."}`

### 3.3 前端页面（Role D Playground）
1. 启动：`cd frontend && npm run dev`，打开页面
2. WS 流式：
   - 点击“连接WS”
   - 输入 `课程介绍` 并“发送”
   - 预期：输出区域看到分片输出，建议问题显示为3条标签，Sources区域有列表（若后端返回）
3. SSE 流式：点击“SSE 查询”，预期输出区域持续追加内容，最终出现 `[END]`
4. 指标与热加载：点击“加载指标/热加载配置”，预期输出区域出现状态行，指标区域更新

## 4. 验收标准
- 数据：fixtures/mock_xzh 三个文件齐全，README中有对应MD5与行数记录
- 后端：上述接口均可调用，返回结构与事件顺序满足预期；安全过滤能阻断恶意文本
- 前端：
  - WS 与 SSE 模式均可正常显示流式内容
  - 建议问题显示三条候选
  - 指标面板能展示命中率字段
  - 热加载按钮返回成功状态
- 偏差处理：若 DeepSeek 网络不可用，Mock 路径（课程介绍）仍能完成端到端的演示

## 5. 回归建议
- 切换提示词版本（修改 `backend/app/core/prompts/qa_prompts.json` 的 default_version 或在服务中切换 current_prompt_version），再次进行 3.2/3.3 验证，确保输出风格变化但流程与结构稳定
- 断开重连场景：在WS流式过程中关闭连接并重连，再次发送查询应能获得完整响应

