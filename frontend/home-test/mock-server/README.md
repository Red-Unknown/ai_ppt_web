# PPT解析API Mock服务器

为前端单独测试PPT解析全流程API而设计的Mock服务。

## 功能特性

- ✅ **完整API模拟**：完全按照 `docs/ppt-parser-api.md` 规范实现
- ✅ **WebSocket支持**：模拟实时流式响应
- ✅ **多种测试场景**：支持正常流程和各种错误场景
- ✅ **可视化测试页面**：内置美观的测试界面
- ✅ **进度模拟**：TTS进度条逐页更新
- ✅ **快速测试模式**：5页快速验证前端逻辑

## 支持的接口

### WebSocket 接口

```
ws://127.0.0.1:8001/api/v1/ws/script
```

服务名：`full_pipeline`

### HTTP 端点

- `GET /health` - 健康检查
- `GET /api/v1/info` - API信息
- `GET /test/` - 可视化测试页面

## 快速开始

### 1. 安装依赖

```bash
cd mock-server
npm install
```

### 2. 启动服务

**Windows:**
```bash
start.bat
```

**或手动启动:**
```bash
npm start
```

### 3. 访问测试页面

打开浏览器访问：
```
http://127.0.0.1:8001/test/
```

## 请求参数

### 标准请求格式

```json
{
  "service": "full_pipeline",
  "file_path": "sandbox/第九章 压杆稳定.ppt",
  "file_type": "ppt",
  "output_raw_json_path": "sandbox/output.json",
  "output_text_path": "sandbox/output.txt",
  "lesson_id": "test_001",
  "course_id": "course_mechanics_001",
  "school_id": "SCH001",
  "title": "第九章 压杆稳定",
  "voice": "zh-CN-XiaoxiaoNeural",
  "enable_script_llm": true
}
```

### 测试专用参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `simulate_pages` | number | 模拟页数（默认65） |
| `mode` | string | `fast` 快速模式（5页） |
| `simulate_error` | string | 模拟错误场景 |

### 错误场景

- `validation` - 验证错误（course_id不存在）
- `parse` - 解析错误
- `tts` - TTS服务错误
- `qdrant` - Qdrant索引错误

## 响应事件流

### 正常流程事件顺序

1. `connection` - 连接成功
2. `status/start` - 开始执行
3. `status/vl_llm_parse_complete` - 解析完成
4. `status/content_text` - 文本提取完成
5. `status/script` - 讲稿生成完成
6. `status/postgres_cir_base` - PostgreSQL插入完成
7. `status/mind_map` - 思维导图生成完成
8. `progress/tts` - TTS进度（多条）
9. `status/tts_done` - TTS完成
10. `status/qdrant` - Qdrant索引完成
11. `done/end` - 流程结束

### 事件格式示例

```json
// 状态更新
{
  "type": "status",
  "step": "vl_llm_parse_complete",
  "path": "sandbox/output.json",
  "message": "课件解析完成（含图片理解）"
}

// 进度更新
{
  "type": "progress",
  "step": "tts",
  "current": 5,
  "total": 65
}

// 完成
{
  "type": "done",
  "step": "end",
  "elapsed_seconds": 45.234,
  "summary": {
    "total_pages": 65,
    "nodes_inserted": 71,
    "keywords_extracted": 30
  }
}

// 错误
{
  "type": "error",
  "step": "validate_course",
  "error": "course_id 不存在",
  "error_type": "CourseNotFoundError"
}
```

## 在前端项目中使用

### 1. 修改API服务配置

在 `src/services/apiService.js` 中添加Mock服务支持：

```javascript
// 使用Mock服务
const USE_MOCK = process.env.VUE_APP_USE_MOCK === 'true';
const WS_URL = USE_MOCK 
  ? 'ws://127.0.0.1:8001/api/v1/ws/script'
  : 'ws://localhost:8001/api/v1/ws/script';
```

### 2. 创建PPT解析服务

```javascript
// src/services/pptParserService.js
export class PPTParserService {
  constructor() {
    this.ws = null;
    this.messageHandlers = new Map();
  }

  connect(url = 'ws://127.0.0.1:8001/api/v1/ws/script') {
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => console.log('WebSocket已连接');
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    return new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });
  }

  handleMessage(data) {
    const handler = this.messageHandlers.get(data.type);
    if (handler) handler(data);
  }

  on(type, handler) {
    this.messageHandlers.set(type, handler);
  }

  parsePPT(requestData) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(requestData));
    }
  }

  disconnect() {
    this.ws?.close();
  }
}
```

### 3. 在组件中使用

```vue
<template>
  <div>
    <button @click="startParsing">开始解析</button>
    <div>进度: {{ progress }}%</div>
    <div>状态: {{ status }}</div>
  </div>
</template>

<script>
import { PPTParserService } from '@/services/pptParserService';

export default {
  data() {
    return {
      parser: new PPTParserService(),
      progress: 0,
      status: ''
    };
  },
  
  async mounted() {
    await this.parser.connect();
    
    this.parser.on('status', (data) => {
      this.status = data.step;
    });
    
    this.parser.on('progress', (data) => {
      if (data.step === 'tts') {
        this.progress = Math.round((data.current / data.total) * 100);
      }
    });
    
    this.parser.on('done', (data) => {
      this.status = '完成';
      console.log('总耗时:', data.elapsed_seconds, '秒');
    });
    
    this.parser.on('error', (data) => {
      this.status = '错误: ' + data.error;
    });
  },
  
  methods: {
    startParsing() {
      this.parser.parsePPT({
        service: 'full_pipeline',
        file_path: 'test.ppt',
        file_type: 'ppt',
        output_raw_json_path: 'output.json',
        output_text_path: 'output.txt',
        course_id: 'test_course'
      });
    }
  },
  
  beforeUnmount() {
    this.parser.disconnect();
  }
};
</script>
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MOCK_PORT` | 8001 | 服务端口 |
| `MOCK_HOST` | 127.0.0.1 | 服务地址 |

## 项目结构

```
mock-server/
├── data/
│   └── mockData.js       # 模拟数据生成器
├── public/
│   └── index.html        # 可视化测试页面
├── server.js             # Mock服务器主文件
├── package.json          # 项目配置
├── start.bat            # Windows启动脚本
└── README.md            # 说明文档
```

## 常见问题

### Q: 如何修改模拟延迟时间？

A: 编辑 `data/mockData.js` 中的 `MOCK_CONFIG.delays` 配置。

### Q: 如何添加新的错误场景？

A: 在 `data/mockData.js` 的 `generateErrorResponse` 函数中添加新的错误类型。

### Q: 前端如何切换到真实后端？

A: 修改环境变量或配置文件中的 WebSocket 地址即可。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持完整的PPT解析流程模拟
- 支持多种错误场景测试
- 内置可视化测试页面
