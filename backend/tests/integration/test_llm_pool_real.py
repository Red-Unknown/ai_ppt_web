import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(ROOT_DIR))

from app.utils.llm_pool import (
    initialize_pool,
    get_llm_client,
    release_llm_client,
    get_pool_status,
    shutdown_pool,
)

async def test_parallel_calls():
    print("=" * 50)
    print("Testing LLM Connection Pool with Real API")
    print("=" * 50)
    
    initialize_pool()
    print("✓ Pool initialized")
    
    status = get_pool_status()
    print(f"✓ Pool config: max_connections={status['config']['max_connections']}")
    print(f"✓ Scenario configs: {list(status['scenarios'].keys())}")
    
    async def call_llm(task_id: int):
        client = get_llm_client("qa", timeout=30.0)
        try:
            from langchain_core.messages import HumanMessage
            response = await client.ainvoke([
                HumanMessage(content="Say 'Hello' in one word")
            ])
            print(f"Task {task_id}: ✓ Success - {response.content[:50]}")
            return True
        except Exception as e:
            print(f"Task {task_id}: ✗ Error - {str(e)[:100]}")
            return False
        finally:
            release_llm_client(client)
    
    print("\n--- Running 5 parallel calls ---")
    tasks = [call_llm(i) for i in range(5)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    print(f"\n--- Results: {success_count}/5 succeeded ---")
    
    final_status = get_pool_status()
    print(f"✓ Final pool status: {final_status['scenarios']}")
    
    shutdown_pool()
    print("✓ Pool shutdown")
    
    return success_count == 5

if __name__ == "__main__":
    result = asyncio.run(test_parallel_calls())
    sys.exit(0 if result else 1)
