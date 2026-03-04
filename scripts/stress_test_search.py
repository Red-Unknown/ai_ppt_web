
import asyncio
import os
import time
import logging
import uuid
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.qa.tools.web_search import WebSearchSkill
from backend.app.core.context import session_id_ctx
from backend.app.services.session.manager import SessionManager
from backend.app.core.rate_limiter import tavily_limiter, deepseek_limiter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_single_search(user_id: str, query: str):
    """
    Simulate a single user search request.
    """
    session_id = f"stress_test_{user_id}_{uuid.uuid4().hex[:8]}"
    
    # Initialize session in manager (mock)
    SessionManager._CHAT_SESSIONS[session_id] = {
        "id": session_id,
        "user_id": user_id,
        "history": [],
        "search_used": False
    }
    
    skill = WebSearchSkill()
    token = session_id_ctx.set(session_id)
    
    start_time = time.time()
    try:
        # Execute search
        result = await skill.execute(query, request_id=f"req_{session_id}")
        latency = (time.time() - start_time) * 1000
        
        status = result.get("status", "unknown")
        content = result.get("content", "")
        
        if "Search limit reached" in content:
            # This shouldn't happen if we use unique sessions, unless we are testing re-entry
            return {"status": "blocked", "latency": latency, "error": "Session limit"}
            
        if "error" in status:
            return {"status": "failed", "latency": latency, "error": content}
            
        return {"status": "success", "latency": latency, "results_count": len(result.get("details", {}).get("sources", []))}
        
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        return {"status": "exception", "latency": latency, "error": str(e)}
    finally:
        session_id_ctx.reset(token)

async def run_batch(concurrency: int):
    """
    Run a batch of concurrent search requests.
    """
    logger.info(f"Starting batch with concurrency: {concurrency}")
    
    queries = [
        "latest AI trends 2025",
        "DeepSeek API documentation",
        "Python asyncio tutorial",
        "FastAPI performance optimization",
        "React vs Vue 2025",
        "Tavily search API pricing",
        "LangChain RAG best practices",
        "Docker container security",
        "Kubernetes scaling strategies",
        "PostgreSQL performance tuning",
        "Redis caching patterns",
        "GraphQL vs REST",
        "Microservices architecture patterns",
        "Event-driven architecture",
        "Serverless computing pros cons",
        "WebAssembly future",
        "Rust vs Go performance",
        "Cybersecurity threats 2025",
        "Quantum computing progress",
        "Climate change solutions 2025"
    ]
    
    # Ensure we have enough queries or cycle them
    tasks = []
    for i in range(concurrency):
        query = queries[i % len(queries)]
        tasks.append(run_single_search(f"user_{i}", query))
        
    start_batch = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_batch
    
    # Analyze results
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = sum(1 for r in results if r["status"] != "success")
    latencies = [r["latency"] for r in results]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
    
    logger.info(f"Batch Completed (Concurrency {concurrency}):")
    logger.info(f"  Total Time: {total_time:.2f}s")
    logger.info(f"  Success: {success_count}/{concurrency}")
    logger.info(f"  Failed: {failed_count}/{concurrency}")
    logger.info(f"  Avg Latency: {avg_latency:.2f}ms")
    logger.info(f"  P95 Latency: {p95_latency:.2f}ms")
    logger.info(f"  Max Latency: {max_latency:.2f}ms")
    
    if failed_count > 0:
        logger.warning("Failures detected:")
        for r in results:
            if r["status"] != "success":
                logger.warning(f"  - {r['status']}: {r.get('error', 'Unknown')}")
                
    return results

async def main():
    logger.info("Starting Stress Test for Web Search Parallelism")
    
    # Verify Env Vars
    if not os.environ.get("TAVILY_API_KEY"):
        logger.warning("TAVILY_API_KEY not found in environment. Test might use Mocks or fail.")
        logger.warning("Please run 'setx TAVILY_API_KEY ...' and restart terminal if needed.")
    else:
        logger.info("TAVILY_API_KEY found.")

    # Gradient Stress Test
    concurrency_levels = [5, 10, 20]
    
    for level in concurrency_levels:
        logger.info(f"\n--- Testing Concurrency Level: {level} ---")
        await run_batch(level)
        # Cool down between batches
        await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user.")
