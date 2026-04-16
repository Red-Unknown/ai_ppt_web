import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.services.qa.retrieval.hybrid_engine import HybridSearchEngine, SimpleBM25, SimpleEmbedder


class TestHybridSearch:

    @pytest.fixture
    def engine(self):
        return HybridSearchEngine()

    @pytest.fixture
    def sample_cir_data(self):
        return [
            {
                "node_id": "node_1",
                "node_name": "人工智能发展历史",
                "page_num": 3,
                "key_points": ["图灵测试", "达特茅斯会议"],
                "teaching_content": "人工智能发展历史介绍，包括图灵测试和达特茅斯会议的召开..."
            },
            {
                "node_id": "node_2",
                "node_name": "机器学习定义",
                "page_num": 5,
                "key_points": ["机器学习定义", "监督学习"],
                "teaching_content": "机器学习是人工智能的一个分支，使计算机能够从数据中学习..."
            }
        ]

    def test_embedder_produces_vector(self):
        embedder = SimpleEmbedder()
        vec = embedder.embed_query("测试查询")
        assert len(vec) == 128
        assert all(isinstance(x, float) for x in vec)

    def test_bm25_scores(self):
        corpus = ["这是第一个文档", "这是第二个文档", "第一个文档包含关键词"]
        bm25 = SimpleBM25(corpus)
        scores = bm25.get_scores("第一个")
        assert len(scores) == 3
        assert scores[0] > 0

    @pytest.mark.asyncio
    async def test_hybrid_search_returns_top_k_results(self, engine, sample_cir_data):
        results = engine.search(
            query="什么是机器学习",
            documents=sample_cir_data,
            search_fields=["key_points", "teaching_content"],
            top_k=2
        )

        assert len(results) <= 2
        assert all("score" in r for r in results)

    @pytest.mark.asyncio
    async def test_hybrid_search_scores_are_normalized(self, engine, sample_cir_data):
        results = engine.search(
            query="图灵测试",
            documents=sample_cir_data,
            search_fields=["key_points"],
            top_k=5
        )

        scores = [r["score"] for r in results]
        assert all(0 <= s <= 1 for s in scores)

    @pytest.mark.asyncio
    async def test_hybrid_search_empty_documents(self, engine):
        results = engine.search(
            query="test",
            documents=[],
            search_fields=["content"],
            top_k=5
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_hybrid_search_keyword_matching(self, engine, sample_cir_data):
        results = engine.search(
            query="图灵",
            documents=sample_cir_data,
            search_fields=["key_points", "teaching_content"],
            top_k=5
        )

        assert len(results) > 0
        assert results[0]["node_id"] == "node_1"

    @pytest.mark.asyncio
    async def test_hybrid_search_with_different_weights(self, engine, sample_cir_data):
        results = engine.search(
            query="机器学习",
            documents=sample_cir_data,
            search_fields=["key_points", "teaching_content"],
            top_k=5,
            alpha=0.6,
            beta=0.3,
            gamma=0.1
        )

        assert len(results) > 0
        assert all("score" in r for r in results)

    def test_embedder_deterministic(self):
        embedder = SimpleEmbedder()
        vec1 = embedder.embed_query("测试")
        vec2 = embedder.embed_query("测试")
        assert vec1 == vec2

    def test_bm25_tokenize_english(self):
        bm25 = SimpleBM25(["hello world test"])
        tokens = bm25._tokenize("Hello World TEST")
        assert "hello" in tokens

    def test_bm25_tokenize_chinese(self):
        bm25 = SimpleBM25(["你好世界"])
        tokens = bm25._tokenize("你好")
        assert "你好" in tokens
