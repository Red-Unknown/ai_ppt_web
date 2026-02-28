import asyncio
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from backend.app.services.qa.service import QAService
from backend.app.services.qa.router import DialogueRouter
from backend.app.schemas.qa import Intent
from backend.app.services.student.state_manager import StudentStateManager

async def verify_multi_turn():
    print("\n--- 1. Verifying Multi-turn Dialogue ---")
    service = QAService()
    session_id = "test_session_multi_turn"
    
    # 1. Ask first question
    q1 = "什么是牛顿第二定律？"
    print(f"User: {q1}")
    # Simulate service call (simplified)
    # In real app, QAService would handle history. Let's see if it does.
    # Currently QAService doesn't seem to have a method taking session_id for history...
    # We will check if we can add history support.
    
    # Check State Manager capabilities
    print("Checking State Manager for history storage...")
    try:
        history = StudentStateManager.get_history(session_id)
        print(f"History retrieved: {history}")
    except AttributeError:
        print("FAIL: StudentStateManager has no get_history method.")

async def verify_intent_routing():
    print("\n--- 2. Verifying Intent Routing ---")
    router = DialogueRouter()
    
    queries = [
        ("老师，暂停一下", Intent.CONTROL),
        ("牛顿第二定律公式是什么？", Intent.QA),
        ("太快了，没听懂", Intent.FEEDBACK),
        ("为什么暂停能改变状态？", Intent.QA), # Tricky case: contains "暂停"
    ]
    
    for query, expected in queries:
        result = router.route(query)
        status = "PASS" if result == expected else "FAIL"
        print(f"Query: '{query}' -> Detected: {result} | Expected: {expected} [{status}]")

async def verify_location_rag():
    print("\n--- 3. Verifying Location-Aware RAG ---")
    service = QAService()
    
    query = "本章讲了什么？"
    current_path = "phys101/mechanics/newton"
    
    # We need to see if retriever uses this path
    # Mocking vector search to return items with different paths
    results = service.retriever._get_relevant_documents(
        query, 
        run_manager=None
    )
    
    # Check if reranking logic works (we need to inspect _rerank_by_path output)
    # Since we can't easily spy on internal methods without mocking, we'll check if we can invoke it directly
    
    from langchain_core.documents import Document
    docs = [
        Document(page_content="A", metadata={"path": "other/path", "score": 0.5}),
        Document(page_content="B", metadata={"path": current_path, "score": 0.5})
    ]
    
    reranked = service.retriever._rerank_by_path(docs, current_path)
    print(f"Input: 2 docs (score 0.5). Target Path: {current_path}")
    print(f"Top result path: {reranked[0].metadata['path']}")
    print(f"Top result score: {reranked[0].metadata.get('score')}")
    
    if reranked[0].metadata['path'] == current_path and reranked[0].metadata['score'] > 0.5:
        print("PASS: Location boosting works.")
    else:
        print("FAIL: Location boosting failed.")

async def main():
    await verify_multi_turn()
    await verify_intent_routing()
    await verify_location_rag()

if __name__ == "__main__":
    asyncio.run(main())
