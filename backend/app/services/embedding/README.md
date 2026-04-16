# Embedding Service

基于 BGE-M3 模型的独立嵌入服务，提供文本嵌入功能，支持稠密向量和稀疏向量（lexical weights）。

## 功能特性

- **BGE-M3 模型**: 支持多语言、多功能的嵌入模型
- **向量维度**: 稠密向量 1024 维，稀疏向量支持词权重
- **批处理优化**: 动态批处理队列，提高吞吐量
- **独立部署**: 不依赖主项目，可独立运行
- **配置灵活**: 支持环境变量配置
- **跨平台**: 支持 Windows
- **Docker 支持**: 提供 Dockerfile 用于容器化部署

## 目录结构

```
embedding/
├── main.py              # 主服务入口
├── requirements.txt     # Python 依赖
├── Dockerfile           # Docker 配置
├── start.ps1            # Windows 启动脚本
├── config/
│   ├── __init__.py
│   └── settings.py      # 配置模块
└── server/
    ├── __init__.py
    └── model.py         # 模型处理模块
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- CUDA 12.1+ (如需 GPU 加速)
- NVIDIA GPU (支持 CUDA 的显卡)

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

#### Windows

```powershell
.\start.ps1
```

#### Python 直接运行

```bash
python main.py
```

## 配置说明

### 网络拓扑

服务默认绑定 `0.0.0.0:8000`，可通过以下地址访问：

- 本机: `http://localhost:8000`
- 局域网: `http://<本机IP>:8000`

### 环境变量

服务支持通过环境变量进行配置：

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `EMBEDDING_HOST` | `localhost` | 服务监听地址 |
| `EMBEDDING_PORT` | `8000` | 服务监听端口 |
| `EMBEDDING_MODEL_NAME` | `BAAI/bge-m3` | 模型名称 |
| `EMBEDDING_DEVICE` | `cuda` | 设备 (`cuda`/`cpu`) |
| `EMBEDDING_USE_FP16` | `true` | 是否使用 FP16 (`true`/`false`) |
| `EMBEDDING_MAX_BATCH_SIZE` | `32` | 最大批处理大小 |
| `EMBEDDING_BATCH_TIMEOUT` | `0.05` | 批处理超时时间（秒） |
| `EMBEDDING_MAX_LENGTH` | `8192` | 最大文本长度 |
| `EMBEDDING_LOG_LEVEL` | `INFO` | 日志级别 |

#### 示例：使用自定义配置启动

```powershell
# Windows
$env:EMBEDDING_PORT = "8080"
$env:EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
$env:EMBEDDING_USE_FP16 = "true"
.\start.ps1
```

## API 接口

### 1. 健康检查

```http
GET /health
```

响应示例：

```json
{
  "status": "healthy",
  "model": "BAAI/bge-m3",
  "device_info": {
    "device": "cuda",
    "model_name": "BAAI/bge-m3",
    "use_fp16": true,
    "gpu_name": "NVIDIA Tesla P100",
    "gpu_memory_allocated": "2.50 GB",
    "gpu_memory_reserved": "3.20 GB"
  }
}
```

### 2. 嵌入接口

```http
POST /embedding
```

请求体：

```json
{
  "data": ["文本1", "文本2", "文本3"],
  "bDense": true,
  "bSparse": true
}
```

参数说明：
- `data` (必填): 需要嵌入的文本列表
- `bDense` (可选): 是否返回稠密向量，默认 `true`
- `bSparse` (可选): 是否返回稀疏向量，默认 `true`

响应示例：

```json
{
  "success": true,
  "data": [
    [0.123, 0.456, ...],
    [0.789, 0.012, ...]
  ],
  "data_sparse": [
    {"word1": 0.5, "word2": 0.3},
    {"word3": 0.4, "word4": 0.6}
  ],
  "meta": {
    "process_time_ms": 150.5,
    "batch_size": 2
  }
}
```

## 使用示例

### Python

```python
import requests

url = "http://localhost:8000/embedding"
data = {
    "data": ["Hello world", "你好世界"],
    "bDense": True,
    "bSparse": True
}

response = requests.post(url, json=data)
result = response.json()

print(result["success"])  # True
print(len(result["data"]))  # 2
```

### QA 模块集成

其他模块调用本服务进行向量嵌入：

```python
import os
import requests

class SimpleEmbedder:
    def __init__(self):
        self.embedding_url = os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:8000/embedding")

    def embed_query(self, text: str):
        response = requests.post(
            self.embedding_url,
            json={"data": [text], "bDense": True, "bSparse": False},
            timeout=30
        )
        return response.json()["data"][0]

    def embed_documents(self, texts: list):
        response = requests.post(
            self.embedding_url,
            json={"data": texts, "bDense": True, "bSparse": False},
            timeout=60
        )
        return response.json()["data"]

embedder = SimpleEmbedder()
vector = embedder.embed_query("Hello world")  # 1024维向量
vectors = embedder.embed_documents(["文本1", "文本2"])  # 批量处理
```

## 错误处理

服务包含完整的错误处理机制：

- **启动错误**: 模型加载失败时显示详细错误信息
- **请求错误**: 返回结构化的错误响应
- **全局异常**: 捕获未处理异常并记录日志

## 性能优化

1. **GPU 加速**: 确保 CUDA 可用以提升推理速度
2. **FP16**: 在支持的 GPU 上启用 FP16 以节省显存
3. **批处理**: 合理调整 `MAX_BATCH_SIZE` 和 `BATCH_TIMEOUT`
4. **批大小**: 根据显存调整模型编码的 `batch_size` 参数
