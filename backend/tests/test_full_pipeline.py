import sys
import asyncio
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

sys.path.insert(0, 'f:/college/sophomore/服务外包')

from sandbox.mock_index_store.index_builder import index_builder
from sandbox.mock_index_store.index_store import memory_index_store
from backend.app.services.qa.retrieval.two_layer_retriever import TwoLayerRetriever
from backend.app.schemas.qa import RetrieveRequest


async def test_full_pipeline():
    print("=" * 80)
    print("FULL PIPELINE TEST: Index Build -> Retrieval API")
    print("=" * 80)

    lesson_id = "lesson_mm_001"
    test_queries = [
        "什么是轴向拉伸",
        "截面法的步骤是什么",
        "胡克定律"
    ]

    print("\n" + "-" * 80)
    print("PHASE 1: Index Building")
    print("-" * 80)

    index_result = await index_builder.build_index_for_lesson(lesson_id)

    print("\n[INDEX BUILD RESULT]")
    print(f"  Lesson ID: {index_result.get('lesson_id')}")
    print(f"  CIR Indexed: {index_result.get('cir_indexed')} documents")
    print(f"  CIR Time: {index_result.get('cir_time_ms', 0):.2f}ms")
    print(f"  RAW Indexed: {index_result.get('raw_indexed')} documents")
    print(f"  RAW Time: {index_result.get('raw_time_ms', 0):.2f}ms")
    print(f"  Total Time: {index_result.get('total_time_ms', 0):.2f}ms")

    if index_result.get('errors'):
        print(f"  Errors: {index_result.get('errors')}")

    stats = memory_index_store.get_stats()
    print(f"\n[INDEX STATS]")
    print(f"  Total Lessons: {stats.get('total_lessons')}")
    print(f"  Total CIR Docs: {stats.get('cir_documents')}")
    print(f"  Total RAW Docs: {stats.get('raw_documents')}")

    print("\n" + "-" * 80)
    print("PHASE 2: Retrieval API Testing")
    print("-" * 80)

    retriever = TwoLayerRetriever()
    results = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}/{len(test_queries)}] {query}")
        print("-" * 40)

        result = await retriever.retrieve(query, lesson_id, top_k=3)

        print(f"  CIR Results: {len(result.get('cir_results', []))}")
        for j, cir in enumerate(result.get('cir_results', [])[:2], 1):
            print(f"    - [{j}] {cir.get('node_name')} (page={cir.get('page_num')}, score={cir.get('score', 0):.3f})")

        print(f"  RAW Results: {len(result.get('raw_results', []))}")
        print(f"  Answer Length: {len(result.get('answer', ''))}")
        print(f"  Bbox Count: {len(result.get('bbox_list', []))}")

        bbox_list = result.get('bbox_list', [])
        if bbox_list:
            print(f"  Bbox Details:")
            for bbox in bbox_list[:3]:
                print(f"    - Page {bbox.get('page_num')}: {len(bbox.get('bboxes', []))} bboxes, merged={bbox.get('is_merged')}")

        results.append({
            "query": query,
            "cir_count": len(result.get('cir_results', [])),
            "raw_count": len(result.get('raw_results', [])),
            "answer": result.get('answer', ''),
            "bbox_count": len(bbox_list)
        })

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for i, r in enumerate(results, 1):
        print(f"\n[{i}] Query: {r['query']}")
        print(f"    CIR: {r['cir_count']}, RAW: {r['raw_count']}, Bbox: {r['bbox_count']}")
        print(f"    Answer: {r['answer'][:80]}..." if len(r['answer']) > 80 else f"    Answer: {r['answer']}")

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
