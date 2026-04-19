# CIR 单层检索设计

## 1. 概述

本文档描述了课程问答系统的检索方案，采用 **单层检索架构**：
- **CIR（Course Intermediate Representation）**：每页 PPT 对应 CIR 的一个节点
- 直接在 CIR 上进行混合搜索，返回答案片段 + Bbox

> **当前实现状态**：Qdrant 未部署，索引构建模块未完成。当前使用内存存储模拟检索，待 Qdrant 部署后可平滑迁移。

## 2. 数据结构

### 2.1 CIR 数据结构 (Course Intermediate Representation)

CIR 是课程中间表示，**每页 PPT 对应 CIR 的一个节点**。

```json
{
  "lesson_id": "lesson_ai_001",
  "school_id": "school_001",
  "lesson_name": "人工智能导论",
  "cir_sections": [
    {
      "node_id": "node_ch1_sec1_page3",
      "lesson_id": "lesson_ai_001",
      "school_id": "school_001",
      "node_name": "1.1 人工智能发展历史",
      "parent_id": "node_ch1",
      "node_type": "subchapter",
      "sort_order": 1,
      "path": "/chapter1/section1",
      "page_num": 3,
      "image_url": "/images/lesson_ai_001/page_3.png",
      "bbox": [0.1, 0.2, 0.8, 0.5],
      "key_points": ["图灵测试", "达特茅斯会议", "第一次AI寒冬", "深度学习突破", "大语言模型"],
      "teaching_content": "第一章 机器学习概述\n\n1.1 人工智能发展历史\n\n一、图灵测试\n1950年，艾伦·图灵发表了著名论文...",
      "script_content": null,
      "duration_seconds": 480,
      "audio_url": null,
      "media_resources": [
        {"type": "image", "description": "图灵像", "url": "/media/lesson_ai_001/turing_portrait.jpg"}
      ],
      "is_teacher_edited": false
    }
  ]
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `node_id` | string | 节点唯一标识（页码级） |
| `node_type` | string | 节点类型：chapter / subchapter / point |
| `node_name` | string | 节点名称 |
| `page_num` | int/null | 关联的 PPT 页码 |
| `key_points` | array | 知识点列表（用于检索） |
| `teaching_content` | string | 教学内容全文（用于检索） |
| `bbox` | array/null | 答案高亮定位框 [x, y, width, height] |
| `image_url` | string/null | 页面图片 URL |
| `path` | string | 章节路径 |

## 3. 检索流程

### 3.1 整体流程图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户查询                               │
│                    "什么是轴向拉伸？"                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  单层检索：CIR 索引                          │
├─────────────────────────────────────────────────────────────┤
│  输入：用户问题                                             │
│  检索：key_points + teaching_content 向量                 │
│  输出：匹配的 CIR 节点列表                                  │
│         (每页PPT对应一个节点，包含 bbox)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Bbox 融合与返回                          │
├─────────────────────────────────────────────────────────────┤
│  1. 收集检索结果中的 bbox                                   │
│  2. 按页码分组，合并同一页的 bbox                           │
│  3. 返回：answer + bbox_list                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 单层检索实现

```python
async def retrieve(
    query: str,
    lesson_id: str,
    top_k: int = 5
) -> SearchResponse:
    """
    检索 CIR 索引，直接返回匹配的页面

    Args:
        query: 用户问题
        lesson_id: 课件ID
        top_k: 返回前k个相关页面

    Returns:
        匹配的页面列表，包含内容 + bbox
    """
    # 1. 加载 CIR 数据（每页PPT作为一个节点）
    cir_data = await load_cir_data(lesson_id)

    # 2. 检索 CIR（key_points + teaching_content）
    results = await hybrid_search(
        query=query,
        documents=cir_data,
        search_fields=["key_points", "teaching_content"],
        top_k=top_k,
        alpha=0.5,    # 向量权重
        beta=0.3,     # BM25权重
        gamma=0.2     # 关键词权重
    )

    # 3. 收集 bbox 并按页码合并
    blocks_with_bbox = []
    for r in results:
        if r.get("bbox"):
            blocks_with_bbox.append(TextBlockWithBbox(
                content=r.get("teaching_content", ""),
                bbox=Bbox.from_dict(r["bbox"]),
                page_num=r.get("page_num", 0)
            ))

    merged_bboxes = merge_bboxes_by_page(blocks_with_bbox)

    # 4. 提取答案
    answer = await extract_answer(query, results)

    return SearchResponse(
        cir_results=results,
        raw_results=results,
        answer=answer,
        bbox_list=format_bbox_for_response(merged_bboxes),
        sources=results
    )
```

## 4. 混合检索实现

### 4.1 当前实现（内存存储）

> **注意**：当前 Qdrant 未部署，使用内存存储模拟。后续可平滑迁移到 Qdrant。

```python
class HybridSearchEngine:
    """
    混合检索引擎
    支持：Dense(向量) + Sparse(BM25) + Keyword(关键词)
    """

    def __init__(self):
        self.embedder = SimpleEmbedder()
        self.bm25 = None

    def search(
        self,
        query: str,
        documents: List[Dict],
        search_fields: List[str],
        top_k: int = 5,
        alpha: float = 0.5,
        beta: float = 0.3,
        gamma: float = 0.2
    ) -> List[Dict]:
        """
        混合检索主方法

        Args:
            query: 用户查询
            documents: 文档列表
            search_fields: 检索字段列表
            top_k: 返回数量
            alpha: 向量权重
            beta: BM25权重
            gamma: 关键词权重
        """
        # 1. 准备检索内容
        corpus = [self._prepare_doc(d, search_fields) for d in documents]

        # 2. Dense 检索（向量相似度）
        query_embedding = self.embedder.embed_query(query)
        doc_vectors = [self.embedder.embed_query(text) for text in corpus]
        dense_scores = self._cosine_similarity(query_embedding, doc_vectors)

        # 3. Sparse 检索 (BM25)
        if self.bm25 is None or len(self.bm25.corpus) != len(corpus):
            self.bm25 = SimpleBM25(corpus)
        bm25_scores = self.bm25.get_scores(query)

        # 4. Keyword 检索
        keyword_scores = self._keyword_search(query, documents)

        # 5. 归一化分数
        norm_dense = self._normalize_scores(dense_scores)
        norm_bm25 = self._normalize_scores(bm25_scores)

        # 6. 加权融合
        results = []
        for i, doc in enumerate(documents):
            d_score = norm_dense[i] if i < len(norm_dense) else 0
            b_score = norm_bm25[i] if i < len(norm_bm25) else 0
            k_score = keyword_scores[i] if i < len(keyword_scores) else 0

            final_score = alpha * d_score + beta * b_score + gamma * k_score
            results.append({**doc, "score": round(final_score, 4)})

        # 7. 排序返回
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]
```

### 4.2 检索权重配置

| 检索阶段 | alpha (向量) | beta (BM25) | gamma (关键词) | 说明 |
|----------|--------------|-------------|----------------|------|
| CIR 检索 | 0.5 | 0.3 | 0.2 | 更侧重语义理解 |

## 5. Bbox 处理

### 5.1 Bbox 格式

前端要求格式：`[x, y, width, height]` 归一化 0-1

```python
@dataclass
class Bbox:
    x: float      # 0-1
    y: float      # 0-1
    width: float  # 0-1
    height: float # 0-1

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.width, self.height]
```

### 5.2 Bbox 合并算法

```python
def merge_bboxes_by_page(blocks: List[TextBlockWithBbox]) -> List[MergedBboxResult]:
    """
    按页面分组合并 Bbox

    策略：
    1. 先按 page_num 分组
    2. 同一页面内的 bbox 合并为最小包围框
    3. 不同页面的 bbox 保持独立
    """
    from collections import defaultdict
    page_groups = defaultdict(list)

    for block in blocks:
        page_groups[block.page_num].append(block)

    results = []
    for page_num, page_blocks in page_groups.items():
        bboxes = [b.bbox for b in page_blocks if b.bbox]
        if not bboxes:
            continue

        merged = _merge_bbox_list(bboxes)
        results.append(MergedBboxResult(
            page_num=page_num,
            bboxes=bboxes,
            merged_bbox=merged,
            total_area_ratio=merged.width * merged.height
        ))

    return sorted(results, key=lambda x: x.page_num)


def _merge_bbox_list(bboxes: List[Bbox]) -> Bbox:
    """将多个 bbox 合并为最小包围框"""
    min_x = min(b.x for b in bboxes)
    min_y = min(b.y for b in bboxes)
    max_x = max(b.x + b.width for b in bboxes)
    max_y = max(b.y + b.height for b in bboxes)

    return Bbox(
        x=min_x,
        y=min_y,
        width=max_x - min_x,
        height=max_y - min_y
    )
```

## 6. RESTful API 设计

### 6.1 检索接口

```http
POST /api/v1/qa/retrieve
Content-Type: application/json
```

**Request**:
```json
{
  "query": "什么是轴向拉伸？",
  "lesson_id": "lesson_001",
  "top_k": 5,
  "enable_decomposition": false
}
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "answer": "轴向拉伸是指构件承受沿轴线方向的拉力...",
    "bbox_list": [
      {
        "page_num": 3,
        "bboxes": [[0.1, 0.2, 0.5, 0.3]],
        "merged_bbox": [0.1, 0.2, 0.5, 0.3],
        "is_merged": false,
        "total_area_ratio": 0.15
      }
    ],
    "context": {
      "matched_chapters": ["1.1 人工智能发展历史"],
      "source_pages": [3, 5, 7]
    },
    "sources": [
      {
        "node_id": "node_ch1_sec1_page3",
        "content": "轴向拉伸是指构件承受沿轴线方向的拉力...",
        "path": "/chapter1/section1",
        "relevance_score": 0.85,
        "page_num": 3,
        "bbox": [0.1, 0.2, 0.5, 0.3],
        "image_url": "/images/lesson_ai_001/page_3.png"
      }
    ]
  },
  "request_id": "req_abc123"
}
```

### 6.2 接口字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `query` | string | 用户问题（必填） |
| `lesson_id` | string | 课件 ID（必填） |
| `top_k` | int | 返回结果数量，默认 5 |
| `enable_decomposition` | bool | 是否启用查询分解 |

### 6.3 错误响应

```json
{
  "code": 400,
  "message": "缺少必填参数: lesson_id",
  "data": null,
  "request_id": "req_abc123"
}
```

## 7. 测试方案

### 7.1 单元测试

#### 7.1.1 混合检索测试

```python
# tests/unit/test_hybrid_search.py
import pytest
from backend.app.services.qa.retrieval.hybrid_engine import HybridSearchEngine

class TestHybridSearch:

    @pytest.fixture
    def engine(self):
        return HybridSearchEngine()

    @pytest.fixture
    def sample_cir_data(self):
        return [
            {
                "node_id": "node_page3",
                "node_name": "人工智能发展历史",
                "page_num": 3,
                "key_points": ["图灵测试", "达特茅斯会议"],
                "teaching_content": "人工智能发展历史介绍...",
                "bbox": [0.1, 0.2, 0.5, 0.3]
            },
            {
                "node_id": "node_page5",
                "node_name": "机器学习定义",
                "page_num": 5,
                "key_points": ["机器学习定义", "监督学习"],
                "teaching_content": "机器学习是人工智能的一个分支...",
                "bbox": [0.2, 0.3, 0.6, 0.4]
            }
        ]

    def test_hybrid_search_returns_top_k_results(self, engine, sample_cir_data):
        results = engine.search(
            query="什么是机器学习",
            documents=sample_cir_data,
            search_fields=["key_points", "teaching_content"],
            top_k=2
        )

        assert len(results) <= 2
        assert all("score" in r for r in results)

    def test_hybrid_search_scores_are_normalized(self, engine, sample_cir_data):
        results = engine.search(
            query="图灵测试",
            documents=sample_cir_data,
            search_fields=["key_points"],
            top_k=5
        )

        scores = [r["score"] for r in results]
        assert all(0 <= s <= 1 for s in scores)
```

#### 7.1.2 Bbox 合并测试

```python
# tests/unit/test_bbox_utils.py
import pytest
from backend.app.services.qa.retrieval.bbox_utils import merge_bboxes_by_page, Bbox

class TestBboxMerge:

    def test_merge_single_page_bboxes(self):
        blocks = [
            TextBlockWithBbox(page_num=1, bbox=Bbox(0.1, 0.1, 0.2, 0.1), content=""),
            TextBlockWithBbox(page_num=1, bbox=Bbox(0.3, 0.2, 0.2, 0.1), content="")
        ]
        results = merge_bboxes_by_page(blocks)

        assert len(results) == 1
        assert results[0].page_num == 1
        assert results[0].merged_bbox.x == 0.1
        assert results[0].merged_bbox.y == 0.1
        assert results[0].merged_bbox.width == 0.4

    def test_keep_different_pages_separate(self):
        blocks = [
            TextBlockWithBbox(page_num=1, bbox=Bbox(0.1, 0.1, 0.2, 0.1), content=""),
            TextBlockWithBbox(page_num=2, bbox=Bbox(0.3, 0.2, 0.2, 0.1), content="")
        ]
        results = merge_bboxes_by_page(blocks)

        assert len(results) == 2
        assert [r.page_num for r in results] == [1, 2]
```

### 7.2 集成测试

#### 7.2.1 单层检索流程测试

```python
# tests/integration/test_two_layer_retrieval.py
import pytest
from backend.app.services.qa.retrieval.two_layer_retriever import TwoLayerRetriever

class TestSingleLayerRetrieval:

    @pytest.fixture
    def retriever(self):
        return TwoLayerRetriever()

    @pytest.mark.asyncio
    async def test_retrieve_returns_cir_results(self, retriever):
        result = await retriever.retrieve(
            query="什么是轴向拉伸",
            lesson_id="lesson_001",
            top_k=3
        )

        assert "cir_results" in result
        assert "answer" in result

    @pytest.mark.asyncio
    async def test_cir_results_contain_bbox(self, retriever):
        result = await retriever.retrieve(
            query="机器学习",
            lesson_id="lesson_ai_001",
            top_k=3
        )

        for cir in result["cir_results"]:
            assert "page_num" in cir
            assert "bbox" in cir or cir.get("bbox") is None

    @pytest.mark.asyncio
    async def test_bbox_list_is_merged(self, retriever):
        result = await retriever.retrieve(
            query="轴向拉伸",
            lesson_id="lesson_001",
            top_k=3
        )

        bbox_list = result.get("bbox_list", [])
        assert isinstance(bbox_list, list)
```

#### 7.2.2 端到端 API 测试

```python
# tests/e2e/test_retrieval_api.py
import pytest
from httpx import AsyncClient

class TestRetrievalAPI:

    @pytest.mark.asyncio
    async def test_retrieve_endpoint_returns_200(self):
        async with AsyncClient(base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/qa/retrieve",
                json={
                    "query": "什么是机器学习",
                    "lesson_id": "lesson_ai_001",
                    "top_k": 3
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert "answer" in data["data"]
            assert "bbox_list" in data["data"]

    @pytest.mark.asyncio
    async def test_retrieve_missing_lesson_id(self):
        async with AsyncClient(base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/qa/retrieve",
                json={"query": "test"}
            )

            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_retrieve_returns_empty_for_unknown_lesson(self):
        async with AsyncClient(base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/qa/retrieve",
                json={
                    "query": "test",
                    "lesson_id": "nonexistent_lesson"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["answer"] == ""
```

### 7.3 测试数据

使用 `sandbox/cir_sample_ai_intro.json` 作为测试数据。

### 7.4 测试覆盖目标

| 测试类型 | 覆盖率目标 | 关键指标 |
|----------|-----------|----------|
| 单元测试 | > 80% | 混合检索、Bbox 合并 |
| 集成测试 | 100% | 单层检索流程 |
| E2E 测试 | 核心场景 | API 正常/异常 |

## 8. 后续迁移计划

### 8.1 Qdrant 集成

当前使用内存存储，后续迁移到 Qdrant 只需修改检索层：

```python
# 目标：替换为 Qdrant 检索
class QdrantRetriever:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)

    async def search(self, collection: str, query_vector: List[float], filter: dict):
        return self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            query_filter=filter,
            with_payload=True
        )
```

### 8.2 索引构建

CIR 索引构建由上游模块负责，检索模块只需调用加载接口。

## 9. 监控指标

| 指标 | 说明 |
|------|------|
| retrieve_latency | 检索延迟 |
| cir_hit_rate | CIR 索引命中率 |
| bbox_coverage | 返回 bbox 的比例 |
| answer_quality_score | 答案质量评分（可后续收集） |
