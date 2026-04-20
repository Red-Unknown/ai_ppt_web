import sys
import asyncio
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

sys.path.insert(0, 'f:/college/sophomore/服务外包')

from backend.app.services.qa.retrieval.index_builder import index_builder, index_builder as builder


async def test_index_building():
    print("=" * 70)
    print("Testing Index Building with Embedding Service")
    print("=" * 70)

    lesson_id = "lesson_mm_001"

    print(f"\n[TEST] Starting index build for {lesson_id}...")
    result = await builder.build_index_for_lesson(lesson_id)

    print("\n" + "=" * 70)
    print("INDEX BUILD RESULT:")
    print("=" * 70)
    print(f"Lesson ID: {result.get('lesson_id')}")
    print(f"CIR Indexed: {result.get('cir_indexed')} documents")
    print(f"CIR Time: {result.get('cir_time_ms', 0):.2f}ms")
    print(f"RAW Indexed: {result.get('raw_indexed')} documents")
    print(f"RAW Time: {result.get('raw_time_ms', 0):.2f}ms")
    print(f"Total Time: {result.get('total_time_ms', 0):.2f}ms")

    if result.get('errors'):
        print(f"\nErrors: {result.get('errors')}")

    stats = builder.get_index_stats(lesson_id)
    print("\n" + "=" * 70)
    print("INDEX STATS:")
    print("=" * 70)
    print(f"Global Stats: {stats.get('global_stats')}")
    print(f"Metadata: {stats.get('metadata')}")

    print("\n[TEST] Index building test completed!")


async def test_embedding_direct():
    print("\n" + "=" * 70)
    print("Testing Direct Embedding Service Call")
    print("=" * 70)

    test_texts = [
        "什么是轴向拉伸",
        "材料力学是研究构件强度、刚度和稳定性的科学",
        "胡克定律描述了弹性范围内的应力-应变关系"
    ]

    try:
        import httpx
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"\n[TEST] Calling embedding service with {len(test_texts)} texts...")
            response = await client.post(
                "http://localhost:8000/embedding",
                json={
                    "data": test_texts,
                    "bDense": True,
                    "bSparse": True
                }
            )

            print(f"[TEST] Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"[TEST] Success: {result.get('success')}")

                if result.get('data'):
                    dense_count = len(result['data'])
                    print(f"[TEST] Dense vectors: {dense_count}")
                    if dense_count > 0:
                        print(f"[TEST] First vector dimension: {len(result['data'][0])}")
                        print(f"[TEST] First vector preview: {result['data'][0][:5]}...")

                if result.get('data_sparse'):
                    sparse_count = len(result['data_sparse'])
                    print(f"[TEST] Sparse vectors: {sparse_count}")

                meta = result.get('meta', {})
                print(f"[TEST] Process time: {meta.get('process_time_ms', 0)}ms")
                print(f"[TEST] Batch size: {meta.get('batch_size', 0)}")
            else:
                print(f"[TEST] Error: {response.text}")

    except httpx.ConnectError as e:
        print(f"[TEST] Connection error: {e}")
    except Exception as e:
        print(f"[TEST] Error: {e}")


if __name__ == "__main__":
    print("Starting tests...\n")
    asyncio.run(test_embedding_direct())
    print("\n" + "=" * 70)
    asyncio.run(test_index_building())
