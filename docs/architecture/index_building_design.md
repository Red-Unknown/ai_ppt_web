# CIR 单层索引构建设计

## 1. 概述

本文档描述了课程问答系统的索引构建方案，采用 **CIR 单层索引** 架构：
- **CIR 索引**：每页 PPT 对应 CIR 的一个节点，包含页面内容 + Bbox 信息

## 2. 数据源

### 2.1 CIR (cir_sections)

课程中间表示数据，**每页 PPT 对应一个节点**：

```json
{
  "lesson_id": "lesson_xxx",
  "cir_sections": [
    {
      "node_id": "node_page3",
      "node_type": "subchapter",
      "page_num": 3,
      "key_points": ["知识点1", "知识点2"],
      "teaching_content": "完整的教学内容文本...",
      "bbox": [0.1, 0.2, 0.8, 0.5],
      "image_url": "/images/lesson_xxx/page_3.png",
      "path": "/chapter1/section1"
    }
  ]
}
```

## 3. 索引设计

### 3.1 Collection 设计

使用 **Qdrant**，创建单个 Collection：

#### Collection: `cir_index`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | node_id |
| lesson_id | string | 所属课件 |
| school_id | string | 学校ID |
| node_type | string | chapter/subchapter/point |
| node_name | string | 节点名称 |
| parent_id | string | 父节点ID |
| page_num | int | 对应PPT页码 |
| key_points | string[] | LLM提取的知识点 |
| teaching_content | string | 完整教学内容 |
| bbox | object | 坐标 {x, y, width, height} |
| image_url | string | 页面图片URL |
| path | string | 章节路径 |
| vector | float[] | teaching_content 向量 (1024维) |

### 3.2 数据模型

```
CIR 节点（每页PPT）
    │
    ├── page_num: 页码
    ├── teaching_content: 页面内容
    ├── key_points: 知识点
    ├── bbox: 答案定位框
    └── image_url: 页面图片
```

## 4. 构建流程

### 4.1 流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    索引构建流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐  │
│  │    CIR      │    │   LLM       │    │ Embedding  │  │
│  │cir_sections │    │ (提取内容)   │    │   Service  │  │
│  └──────┬───────┘    └──────┬───────┘    └─────┬──────┘  │
│         │                    │                   │          │
│         │  提取页面内容      │  提取关键内容     │          │
│         ▼                    ▼                   │          │
│  ┌──────────────────────────────────────────────┐         │
│  │              数据预处理层                       │         │
│  │  1. 解析 CIR sections                      │         │
│  │  2. 提取 teaching_content + key_points    │         │
│  │  3. 保留 bbox 和 image_url                │         │
│  └──────────────────────┬───────────────────────┘         │
│                         │                                   │
│                         │ 调用embedding服务                  │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────┐         │
│  │              向量生成层                         │         │
│  │  - CIR: teaching_content → vector           │         │
│  └──────────────────────┬───────────────────────┘         │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────┐         │
│  │              Qdrant 存储层                    │         │
│  │  ┌─────────────────────────────────────┐    │         │
│  │  │         cir_index Collection         │    │         │
│  │  │  (每页PPT一个向量)                    │    │         │
│  │  └─────────────────────────────────────┘    │         │
│  └──────────────────────────────────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 详细步骤

#### Step 1: 加载 CIR 数据
```python
def load_cir_sections(lesson_id: str) -> List[CIRSection]:
    """从数据库或文件加载 CIR 数据"""
    db = SessionLocal()
    sections = db.query(CIRSectionModel).filter(
        CIRSectionModel.lesson_id == lesson_id
    ).all()
    return sections
```

#### Step 2: 预处理数据
```python
def preprocess_cir(sections: List[CIRSection]) -> List[Dict]:
    """预处理 CIR 数据，生成检索文档"""
    documents = []
    for section in sections:
        doc = {
            "id": section.node_id,
            "lesson_id": section.lesson_id,
            "school_id": section.school_id,
            "node_type": section.node_type,
            "node_name": section.node_name,
            "parent_id": section.parent_id,
            "page_num": section.page_num,
            "key_points": section.key_points or [],
            "teaching_content": section.teaching_content or "",
            "bbox": section.bbox,
            "image_url": section.image_url,
            "path": section.path or ""
        }
        documents.append(doc)
    return documents
```

#### Step 3: 向量化
```python
def vectorize_documents(documents: List[Dict], embed_service) -> List[Dict]:
    """调用 embedding 服务生成向量"""
    texts = [doc["teaching_content"] for doc in documents]
    vectors = embed_service.encode(texts)
    
    for doc, vector in zip(documents, vectors):
        doc["vector"] = vector
    return documents
```

#### Step 4: 存储到 Qdrant
```python
def save_to_qdrant(collection, documents: List[Dict]):
    """存储到 Qdrant"""
    points = [
        PointStruct(
            id=doc["id"],
            vector=doc["vector"],
            payload={
                "lesson_id": doc["lesson_id"],
                "school_id": doc["school_id"],
                "node_type": doc["node_type"],
                "node_name": doc["node_name"],
                "parent_id": doc.get("parent_id"),
                "page_num": doc.get("page_num"),
                "key_points": doc.get("key_points", []),
                "teaching_content": doc.get("teaching_content", ""),
                "bbox": doc.get("bbox"),
                "image_url": doc.get("image_url"),
                "path": doc.get("path", "")
            }
        )
        for doc in documents if doc.get("vector")
    ]
    collection.upsert(points)
```

## 5. 索引更新策略

### 5.1 全量重建

适用于：课件首次导入、重大结构变更

```python
def rebuild_index(lesson_id: str):
    """全量重建索引"""
    # 1. 删除旧索引
    qdrant.delete(f"cir_{lesson_id}")
    
    # 2. 重新构建
    build_index(lesson_id)
```

### 5.2 增量更新

适用于：单页PPT修改、知识点更新

```python
def update_index(lesson_id: str, node_id: str, updates: Dict):
    """增量更新单页索引"""
    # 更新 cir_index 中该节点数据
    # 1. 重新生成向量
    # 2. 更新 Qdrant 中的 point
```

### 5.3 删除索引

```python
def delete_index(lesson_id: str):
    """删除课件索引"""
    qdrant.delete(f"cir_{lesson_id}")
```

## 6. 配置参数

### 6.1 Qdrant 配置

```yaml
qdrant:
  host: "localhost"
  port: 6333
  collections:
    cir_index:
      vector_size: 1024  # BGE-M3 稠密向量维度
      distance: "Cosine"
```

### 6.2 Embedding 服务配置

基于现有 embedding 服务（`backend/app/services/embedding/README.md`）：

```yaml
embedding:
  service_url: "http://localhost:8000"
  model: "BAAI/bge-m3"
  device: "cuda"  # 或 cpu
  batch_size: 32
  max_length: 8192
  use_fp16: true
```

#### Embedding 服务调用示例

```python
import requests

EMBEDDING_URL = "http://localhost:8000/embedding"

def encode_texts(texts: List[str]) -> List[List[float]]:
    """调用 embedding 服务生成向量"""
    response = requests.post(
        EMBEDDING_URL,
        json={
            "data": texts,
            "bDense": True,
            "bSparse": False
        }
    )
    result = response.json()
    if result.get("success"):
        return result["data"]
    else:
        raise Exception(f"Embedding failed: {result}")
```

#### 关键配置说明

| 参数 | 值 | 说明 |
|------|-----|------|
| vector_size | 1024 | BGE-M3 稠密向量维度 |
| service_url | http://localhost:8000 | embedding 服务地址 |
| model | BAAI/bge-m3 | 多语言嵌入模型 |
| batch_size | 32 | 根据显存调整 |
| bDense | true | 返回稠密向量 |
| bSparse | false | 本场景不需要稀疏向量 |

## 7. 检索集成

检索时直接查询 CIR 索引：

```python
async def retrieve_cir(
    query: str,
    lesson_id: str,
    top_k: int = 5
) -> List[Dict]:
    """检索 CIR 索引"""
    # 1. 生成查询向量
    query_vector = embed_service.encode([query])[0]
    
    # 2. 查询 Qdrant
    results = qdrant.search(
        collection_name="cir_index",
        query_vector=query_vector,
        query_filter={
            "must": [
                {"key": "lesson_id", "match": {"value": lesson_id}}
            ]
        },
        limit=top_k,
        with_payload=True
    )
    
    # 3. 解析结果
    return [
        {
            "node_id": r.payload["node_id"],
            "node_name": r.payload["node_name"],
            "page_num": r.payload["page_num"],
            "key_points": r.payload["key_points"],
            "teaching_content": r.payload["teaching_content"],
            "bbox": r.payload["bbox"],
            "image_url": r.payload["image_url"],
            "path": r.payload["path"],
            "score": r.score
        }
        for r in results
    ]
```

## 8. 错误处理

| 场景 | 处理策略 |
|------|----------|
| CIR 数据解析失败 | 跳过该节点，记录日志 |
| Embedding 服务不可用 | 缓存文本，等待重试 |
| Qdrant 连接失败 | 返回错误，前端提示 |
| Bbox 缺失 | 返回 null，前端不展示高亮 |
| 页面内容为空 | 不创建索引节点 |

## 9. 监控指标

| 指标 | 说明 |
|------|------|
| index_build_duration | 索引构建耗时 |
| vectorize_latency | 向量化延迟 |
| total_vectors | 向量总数 |
| storage_size | 存储大小 |
| index_coverage | 索引覆盖率（有内容的页面比例） |
