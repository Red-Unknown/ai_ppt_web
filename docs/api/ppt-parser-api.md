# PPT 解析全流程 WebSocket API

## 1. 接口说明

- **用途**：PPT 上传后触发全流程解析（解析 -> 文本提取 -> mind_map -> script -> tts -> qdrant -> done）
- **协议**：WebSocket
- **地址**：`ws://127.0.0.1:8001/api/v1/ws/script`
- **后端入口**：`backend/app/api/v1/ws_script.py`
- **服务名**：`full_pipeline`

---

## 2. 前端首帧请求

连接成功后第一条消息必须是 JSON：

```json
{
  "service": "full_pipeline",
  "file_path": "sandbox/第九章 压杆稳定.ppt",
  "file_type": "ppt",
  "output_raw_json_path": "sandbox/第九章 压杆稳定_全流程测试.json",
  "output_text_path": "sandbox/第九章 压杆稳定_全流程测试.txt",
  "lesson_id": "parse_e2e_test_001",
  "course_id": "course_mechanics_001",
  "school_id": "SCH001",
  "title": "第九章 压杆稳定",
  "voice": "zh-CN-XiaoxiaoNeural",
  "enable_script_llm": true
}
```

### 字段说明

- `service`：固定 `full_pipeline`
- `file_path`：输入课件路径（必填）
- `file_type`：`ppt` / `pptx` / `pdf`（必填）
- `output_raw_json_path`：解析结果 JSON 输出路径（必填）
- `output_text_path`：文本抽取输出路径（必填）
- `lesson_id`：本次任务ID（建议唯一，避免覆盖）
- `course_id`：课程ID（必填，且必须存在于 `courses`）
- `school_id`：学校ID（与课程记录匹配）
- `title`：课件标题
- `voice`：TTS 音色
- `enable_script_llm`：是否启用 LLM 讲稿生成开关

---

## 3. 服务端事件流（yield）

客户端将持续收到事件，直到 `done` 或 `error`。

### 3.1 正常顺序

1. `status/start`
2. `status/vl_llm_parse_complete`
3. `status/content_text`
4. `status/script`
5. `status/postgres_cir_base`
6. `status/mind_map`
7. `progress/tts`（多条，`current` 递增）
8. `status/tts_done`
9. `status/qdrant`
10. `done/end`

### 3.2 事件示例

```json
{"type":"status","step":"start","message":"开始执行全流程"}
{"type":"status","step":"vl_llm_parse_complete","path":"sandbox\\第九章 压杆稳定_全流程测试.json","lesson_id":"parse_e2e_test_001","message":"课件解析完成（含图片理解）"}
{"type":"status","step":"content_text","pages":65,"path":"sandbox\\第九章 压杆稳定_全流程测试.txt"}
{"type":"status","step":"script","generated":65,"llm":false}
{"type":"status","step":"postgres_cir_base","inserted_nodes":66}
{"type":"status","step":"mind_map","keywords_count":30}
{"type":"progress","step":"tts","current":1,"total":65}
{"type":"progress","step":"tts","current":65,"total":65}
{"type":"status","step":"tts_done"}
{"type":"status","step":"qdrant","ok":true,"log":"[INFO] ... [DONE] Qdrant ingestion finished."}
{"type":"done","step":"end","lesson_id":"parse_e2e_test_001","elapsed_seconds":187.355}
```

### 3.3 错误事件

```json
{"type":"error","step":"validate_course","error":"course_id 不存在: course_xxx。请先在 courses 表创建该课程。"}
```

或

```json
{"type":"error","error":"错误详情","error_type":"ExceptionType"}
```

---

## 4. 运行产物与落库

### 文件产物

- `output_raw_json_path`：结构化解析结果（含图片理解）
- `output_text_path`：按页内容文本

### PostgreSQL

- `lessons`：任务状态、文件信息、mind_map、完成时间
- `cir_sections`：章节树、讲稿内容、TTS 任务地址

### Qdrant

- 集合：`cir_index`
- 按 `lesson_id` 重建并 upsert 向量点

---

## 5. 前置条件（联调必备）

- 后端服务已启动：`8001`
- `course_id` 在 `courses` 中存在，且与 `school_id` 匹配
- Qdrant 可访问（默认 `6333`）
- embedding 服务可访问（建议通过环境变量配置）
  - `EMBEDDING_SERVICE_URL=http://10.0.0.3:8000/embedding`
- 图片解析模型与文本模型密钥已配置

---

## 6. 典型联调命令（测试脚本）

```powershell
& "D:\Anaconda\envs\ai_ppt_web\python.exe" scripts/test_full_pipeline_ws.py --course-id "course_mechanics_001" --school-id "SCH001"
```

---

## 7. 已验证结果（本地实测）

- 全流程已跑通至 `done`
- `qdrant.ok` 已验证可达 `true`
- 返回包含完整 `tts` 进度与总耗时
