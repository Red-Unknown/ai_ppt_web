# 异步文字转语音API文档

## 概述

异步文字转语音API提供高并发支持的语音合成服务，采用任务队列模式处理请求，支持最大10个并发任务处理。

## 基础URL

```
http://localhost:8000/api/v1/async-tts
```

## API端点

### 1. 提交语音合成任务

**POST** `/synthesize`

提交异步语音合成任务，返回任务ID供后续查询。

#### 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | 是 | - | 要合成的文本内容（支持数学公式转换） |
| voice | string | 否 | zh-CN-XiaoxiaoNeural | 语音标识 |
| client_id | string | 否 | default | 客户端标识（用于限流） |

#### 支持的语音

| 语言 | 语音标识 | 说明 |
|------|----------|------|
| 中文女声 | zh-CN-XiaoxiaoNeural | 晓晓（默认） |
| 中文男声 | zh-CN-YunyangNeural | 云扬 |
| 中文女声 | zh-CN-XiaoyiNeural | 小艺 |
| 英文女声 | en-US-AriaNeural | Aria |
| 英文男声 | en-US-GuyNeural | Guy |

#### 成功响应 (202 Accepted)

```json
{
    "status": "accepted",
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "任务已提交，正在处理中",
    "remaining_requests": 95
}
```

#### 错误响应 (429 Too Many Requests)

```json
{
    "error": "rate_limit_exceeded",
    "message": "请求过于频繁，请稍后重试",
    "reset_time": "2024-01-01T12:01:00Z"
}
```

---

### 2. 查询任务状态

**GET** `/status/{task_id}`

查询语音合成任务的状态和进度。

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |

#### 响应示例

```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "progress": 50,
    "message": "正在生成语音...",
    "created_at": "2024-01-01T12:00:00Z",
    "started_at": "2024-01-01T12:00:01Z",
    "duration_ms": null
}
```

#### 状态说明

| 状态 | 说明 |
|------|------|
| pending | 任务等待处理 |
| processing | 正在生成语音 |
| completed | 语音生成完成 |
| failed | 语音生成失败 |

---

### 3. 获取语音合成结果

**GET** `/result/{task_id}`

获取语音合成结果（MP3音频文件）。

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |

#### 成功响应

- Content-Type: `audio/mpeg`
- 返回MP3格式的音频数据

#### 错误响应 (400 Bad Request)

```json
{
    "error": "task_not_completed",
    "message": "任务尚未完成，请先查询状态确认",
    "current_status": "processing"
}
```

---

### 4. 取消任务

**DELETE** `/task/{task_id}`

取消等待中的任务。

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |

#### 成功响应

```json
{
    "success": true,
    "message": "任务已取消"
}
```

#### 错误响应 (400 Bad Request)

```json
{
    "error": "cannot_cancel",
    "message": "无法取消该任务（可能已在处理或已完成）"
}
```

---

### 5. 获取服务统计

**GET** `/stats`

获取异步TTS服务的统计信息。

#### 响应示例

```json
{
    "queue": {
        "total_tasks": 15,
        "pending_tasks": 3,
        "processing_tasks": 5,
        "completed_tasks": 7,
        "failed_tasks": 0,
        "active_workers": 5,
        "max_concurrent": 10
    },
    "rate_limit": {
        "total_active_clients": 12,
        "total_requests_in_window": 156,
        "max_requests_per_client": 100,
        "time_window_seconds": 60
    },
    "service_running": true
}
```

---

### 6. 阻塞等待任务完成

**GET** `/wait/{task_id}?timeout=60`

阻塞等待任务完成（最长等待timeout秒）。

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| task_id | string (path) | 是 | - | 任务ID |
| timeout | int (query) | 否 | 60 | 最长等待时间（1-300秒） |

#### 成功响应

```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "progress": 100,
    "message": "语音生成完成",
    "duration_ms": 2345
}
```

---

## 使用流程

### 流程一：异步模式（推荐）

```
1. POST /synthesize → 获取 task_id
2. 轮询 GET /status/{task_id} → 检查状态
3. 当状态为 completed 时，GET /result/{task_id} → 获取音频
```

### 流程二：同步模式（简单场景）

```
1. POST /synthesize → 获取 task_id
2. GET /wait/{task_id} → 阻塞等待完成
3. GET /result/{task_id} → 获取音频
```

## 限流规则

- 每个客户端每分钟最多100次请求
- 超出限制后需等待时间窗口重置
- 使用 `client_id` 标识不同客户端

## 数学公式支持

API自动将数学符号转换为可读文本：

| 符号 | 转换后 |
|------|--------|
| E=mc² | 能量E等于质量m乘以光速c的平方 |
| π | 派 |
| √ | 根号 |
| ∫ | 积分 |
| ∑ | 求和 |
| x² | x的平方 |
| x₀ | x下标零 |

## 错误处理

| HTTP状态码 | 错误类型 | 说明 |
|------------|----------|------|
| 404 | task_not_found | 任务不存在或已过期 |
| 400 | task_not_completed | 任务尚未完成 |
| 429 | rate_limit_exceeded | 请求过于频繁 |
| 408 | timeout | 等待超时 |

## 代码示例

### Python 异步调用示例

```python
import asyncio
import aiohttp

async def synthesize_speech(text):
    async with aiohttp.ClientSession() as session:
        # 提交任务
        response = await session.post(
            "http://localhost:8000/api/v1/async-tts/synthesize",
            json={"text": text, "voice": "zh-CN-XiaoxiaoNeural"}
        )
        result = await response.json()
        task_id = result["task_id"]
        
        # 轮询状态
        while True:
            response = await session.get(f"http://localhost:8000/api/v1/async-tts/status/{task_id}")
            status = await response.json()
            
            if status["status"] == "completed":
                break
            elif status["status"] == "failed":
                raise Exception(f"任务失败: {status.get('error')}")
            
            await asyncio.sleep(0.5)
        
        # 获取结果
        response = await session.get(f"http://localhost:8000/api/v1/async-tts/result/{task_id}")
        audio_data = await response.read()
        
        return audio_data
```

### cURL 示例

```bash
# 提交任务
curl -X POST http://localhost:8000/api/v1/async-tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "voice": "en-US-AriaNeural"}'

# 查询状态
curl http://localhost:8000/api/v1/async-tts/status/{task_id}

# 获取结果
curl http://localhost:8000/api/v1/async-tts/result/{task_id} -o output.mp3
```

---

## 性能指标

| 指标 | 数值 |
|------|------|
| 最大并发任务数 | 10 |
| 单客户端限流 | 100次/分钟 |
| 任务过期时间 | 1小时 |
| 建议轮询间隔 | 500ms |