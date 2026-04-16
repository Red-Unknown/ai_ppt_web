import sys
sys.path.insert(0, 'f:/college/sophomore/服务外包')

import asyncio
from backend.app.services.qa.retrieval.two_layer_retriever import TwoLayerRetriever
from backend.app.schemas.qa import RetrieveRequest

async def test_retrieval():
    retriever = TwoLayerRetriever()
    request = RetrieveRequest(
        query="什么是轴向拉伸",
        lesson_id="lesson_mm_001",
        top_k=3
    )
    result = await retriever.retrieve(request.query, request.lesson_id, request.top_k)
    print(f"CIR results: {len(result.get('cir_results', []))}")
    print(f"Raw results: {len(result.get('raw_results', []))}")
    print(f"Answer length: {len(result.get('answer', ''))}")
    print(f"Bbox count: {len(result.get('bbox_list', []))}")
    print(f"Sources count: {len(result.get('sources', []))}")

async def test_error_handling():
    retriever = TwoLayerRetriever()
    result = await retriever.retrieve("", "lesson_mm_001", 3)
    print(f"Empty query - CIR results: {len(result.get('cir_results', []))}")

if __name__ == "__main__":
    print("=== Test 1: 正常请求 ===")
    asyncio.run(test_retrieval())
    print("\n=== Test 2: 空查询 ===")
    asyncio.run(test_error_handling())
