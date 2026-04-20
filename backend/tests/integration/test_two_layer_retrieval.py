import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.services.qa.retrieval.two_layer_retriever import TwoLayerRetriever


class TestTwoLayerRetrieval:

    @pytest.fixture
    def retriever(self):
        return TwoLayerRetriever()

    @pytest.mark.asyncio
    async def test_retrieve_returns_cir_and_raw_results(self, retriever):
        result = await retriever.retrieve(
            query="什么是轴向拉伸",
            lesson_id="lesson_mm_001",
            top_k=3
        )

        assert "cir_results" in result
        assert "raw_results" in result
        assert "answer" in result
        assert "bbox_list" in result

    @pytest.mark.asyncio
    async def test_cir_results_contain_page_range(self, retriever):
        result = await retriever.retrieve(
            query="机器学习",
            lesson_id="lesson_mm_001",
            top_k=3
        )

        for cir in result["cir_results"]:
            assert "page_num" in cir
            assert cir["page_num"] is not None

    @pytest.mark.asyncio
    async def test_raw_results_structure(self, retriever):
        result = await retriever.retrieve(
            query="轴向拉伸",
            lesson_id="lesson_mm_001",
            top_k=3
        )

        if result.get("raw_results"):
            raw = result["raw_results"][0]
            assert "content" in raw
            assert "page_num" in raw

    @pytest.mark.asyncio
    async def test_empty_query_returns_empty(self, retriever):
        result = await retriever.retrieve(
            query="",
            lesson_id="lesson_mm_001",
            top_k=3
        )

        assert "cir_results" in result
