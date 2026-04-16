# CIR + Raw JSON 混合索引构建设计

## 1. 概述

本文档描述了课程问答系统的索引构建方案，采用 **CIR + Raw JSON 混合索引** 架构：
- **CIR索引**：用于语义检索，找到相关章节
- **Raw JSON索引**：用于精确返回答案片段 + Bbox

## 2. 数据源

### 2.1 Raw JSON (extract.json)
PPT解析后的原始数据，结构如下：
```json
{
  "structurePreview": {
    "chapters": [{
      "chapterId": "xxx",
      "chapterName": "章节名",
      "subChapters": [{
        "subChapterId": "xxx",
        "subChapterName": "节名",
        "pageRange": "4-6",
        "elements": [{
          "type": "text",
          "content": "文本内容",
          "bbox": {"x": 0.1, "y": 0.2, "width": 0.5, "height": 0.3}
        }]
      }]
    }]
  }
}
```

### 2.2 CIR (cir_sections)
课程中间表示数据，结构如下：
```json
{
  "lesson_id": "lesson_xxx",
  "cir_sections": [{
    "node_id": "node_ch1_sec1",
    "node_type": "subchapter",
    "page_num": 4,
    "key_points": ["知识点1", "知识点2"],
    "teaching_content": "完整的教学内容文本..."
  }]
}
```

## 3. 索引设计

### 3.1 Collection 设计

使用 **Qdrant**，创建两个 Collection：

#### Collection 1: `cir_index`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | node_id |
| lesson_id | string | 所属课件 |
| school_id | string | 学校ID |
| node_type | string | chapter/subchapter |
| node_name | string | 节点名称 |
| parent_id | string | 父节点ID |
| page_num | int | 对应PPT页码 |
| key_points | string[] | LLM提取的知识点 |
| teaching_content | string | 完整教学内容 |
| vector | float[] | teaching_content 向量 (1024维) |

#### Collection 2: `raw_json_index`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 元素唯一ID (pageNum_elementIdx) |
| lesson_id | string | 所属课件 |
| page_num | int | PPT页码 |
| subchapter_id | string | 关联的CIR subchapter ID |
| content | string | 文本内容 |
| bbox | object | 坐标 {x, y, width, height} |
| vector | float[] | content 向量 (1024维) |

### 3.2 关联关系

```
Raw JSON Element
       │
       │ page_num 匹配 CIR page_num
       ▼
  CIR Subchapter
       │
       │ parent_id 追溯
       ▼
  CIR Chapter
```

**关键设计**：通过 `page_num` 建立 Raw JSON 与 CIR 的关联

## 4. 构建流程

### 4.1 流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    索引构建流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐  │
│  │  Raw JSON   │    │    CIR      │    │ Embedding  │  │
│  │ extract.json│    │cir_sections │    │   Service  │  │
│  └──────┬───────┘    └──────┬───────┘    └─────┬──────┘  │
│         │                    │                   │          │
│         │  提取文本块        │  提取章节信息      │          │
│         ▼                    ▼                   │          │
│  ┌──────────────────────────────────────────────┐         │
│  │              数据预处理层                       │         │
│  │  1. 解析 raw json elements                  │         │
│  │  2. 关联 CIR subchapter (通过 page_num)     │         │
│  │  3. 生成元素唯一ID                          │         │
│  └──────────────────────┬───────────────────────┘         │
│                         │                                   │
│                         │ 调用embedding服务                  │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────┐         │
│  │              向量生成层                         │         │
│  │  - raw_json: content → vector                │         │
│  │  - cir: teaching_content → vector            │         │
│  └──────────────────────┬───────────────────────┘         │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────┐         │
│  │              Qdrant 存储层                    │         │
│  │  ┌─────────────┐      ┌─────────────┐        │         │
│  │  │ cir_index   │      │raw_json_idx │        │         │
│  │  │ Collection  │      │ Collection  │        │         │
│  │  └─────────────┘      └─────────────┘        │         │
│  └──────────────────────────────────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 详细步骤

#### Step 1: 解析 Raw JSON
```python
def parse_raw_json(raw_json_path: str) -> List[RawTextBlock]:
    """解析 extract.json，提取文本块"""
    blocks = []
    for chapter in raw_json['structurePreview']['chapters']:
        for subchapter in chapter['subChapters']:
            page_range = subchapter['pageRange']  # e.g., "4-6"
            pages = parse_page_range(page_range)   # [4, 5, 6]
            
            for element in subchapter['elements']:
                block = RawTextBlock(
                    id=f"page_{element['page_num']}_elem_{idx}",
                    page_num=element['page_num'],
                    content=element['content'],
                    bbox=element.get('bbox'),
                    subchapter_id=subchapter['subChapterId']
                )
                blocks.append(block)
    return blocks
```

#### Step 2: 关联 CIR
```python
def link_cir(blocks: List[RawTextBlock], cir_sections: List[CIRSection]):
    """通过 page_num 关联 CIR subchapter"""
    # 建立 page_num -> subchapter 映射
    page_to_subchapter = {
        sec.page_num: sec.node_id 
        for sec in cir_sections if sec.node_type == 'subchapter'
    }
    
    for block in blocks:
        block.subchapter_id = page_to_subchapter.get(block.page_num)
    return blocks
```

#### Step 3: 向量化
```python
def vectorize_blocks(blocks: List[RawTextBlock], embed_service):
    """调用已有embedding服务生成向量"""
    texts = [block.content for block in blocks]
    vectors = embed_service.encode(texts)
    
    for block, vector in zip(blocks, vectors):
        block.vector = vector
    return blocks
```

#### Step 4: 存储到 Qdrant
```python
def save_to_qdrant(cir_collection, raw_collection, cir_sections, blocks):
    # 1. 存储 CIR 数据
    cir_points = [
        PointStruct(
            id=sec.node_id,
            vector=sec.vector,
            payload={
                "lesson_id": sec.lesson_id,
                "node_type": sec.node_type,
                "node_name": sec.node_name,
                "page_num": sec.page_num,
                "key_points": sec.key_points,
                "teaching_content": sec.teaching_content
            }
        )
        for sec in cir_sections
    ]
    cir_collection.upsert(cir_points)
    
    # 2. 存储 Raw JSON 数据
    raw_points = [
        PointStruct(
            id=block.id,
            vector=block.vector,
            payload={
                "lesson_id": block.lesson_id,
                "page_num": block.page_num,
                "subchapter_id": block.subchapter_id,
                "content": block.content,
                "bbox": block.bbox
            }
        )
        for block in blocks
    ]
    raw_collection.upsert(raw_points)
```

## 5. 索引更新策略

### 5.1 全量重建
适用于：课件首次导入、重大结构变更
```python
def rebuild_index(lesson_id: str):
    """全量重建索引"""
    # 1. 删除旧索引
    qdrant.delete(f"cir_{lesson_id}")
    qdrant.delete(f"raw_{lesson_id}")
    
    # 2. 重新构建
    build_index(lesson_id)
```

### 5.2 增量更新
适用于：单页PPT修改、知识点更新
```python
def update_index(lesson_id: str, page_num: int, elements: List[Dict]):
    """增量更新单页索引"""
    # 1. 更新 raw_json_index 中该页数据
    # 2. 如果涉及知识点变更，更新 cir_index
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
    raw_json_index:
      vector_size: 1024
      distance: "Cosine"
```

### 6.2 Embedding 服务配置

基于现有 embedding 服务（`backend/app/services/embedding/README.md`）：

```yaml
embedding:
  service_url: "http://localhost:8000"  # 或 http://localhost:8000
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
            "bSparse": False  # 本场景只需稠密向量
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

## 7. 错误处理

| 场景 | 处理策略 |
|------|----------|
| Raw JSON 解析失败 | 跳过该元素，记录日志 |
| Embedding 服务不可用 | 缓存文本，等待重试 |
| Qdrant 连接失败 | 返回错误，前端提示 |
| Bbox 缺失 | 返回 null，前端不展示高亮 |

## 8. 监控指标

| 指标 | 说明 |
|------|------|
| index_build_duration | 索引构建耗时 |
| vectorize_latency | 向量化延迟 |
| total_vectors | 向量总数 |
| storage_size | 存储大小 |
