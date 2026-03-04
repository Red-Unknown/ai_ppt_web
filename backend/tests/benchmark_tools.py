
import asyncio
import time
import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.app.services.qa.tools.math_solver import MathSolver
from backend.app.services.qa.tools.web_search import WebSearchSkill
from backend.app.utils.sandbox import SafeCodeExecutor
from backend.app.core.config import settings
from backend.app.core.context import session_id_ctx

# Load environment variables
load_dotenv()

async def benchmark_math_solver():
    print("\n--- Benchmarking MathSolver ---")
    
    # Initialize
    try:
        solver = MathSolver()
        query = "Calculate the sum of the first 100 prime numbers."
        print(f"Query: {query}")
        
        gen_time = 0
        code = ""
        
        # 1. Measure Code Generation
        try:
            start = time.perf_counter()
            raw_code = await solver.code_gen_chain.ainvoke({"query": query})
            code = raw_code.replace("```python", "").replace("```", "").strip()
            gen_time = time.perf_counter() - start
            print(f"[Step 1] Code Generation: {gen_time:.4f}s")
        except Exception as e:
            print(f"[Step 1] Code Generation Failed: {e}")
            print("Using fallback code for execution test.")
            code = "import math\nresult = sum(num for num in range(2, 542) if all(num % i != 0 for i in range(2, int(math.sqrt(num)) + 1)))"
            gen_time = -1

        # 2. Measure Code Execution
        start = time.perf_counter()
        # SafeCodeExecutor.execute is synchronous
        result = SafeCodeExecutor.execute(code)
        exec_time = time.perf_counter() - start
        print(f"[Step 2] Code Execution:  {exec_time:.4f}s")
        
        # 3. Measure Explanation
        explain_time = 0
        try:
            start = time.perf_counter()
            explanation = await solver.explanation_chain.ainvoke({
                "query": query,
                "code": code,
                "result": result
            })
            explain_time = time.perf_counter() - start
            print(f"[Step 3] Explanation Gen: {explain_time:.4f}s")
        except Exception as e:
            print(f"[Step 3] Explanation Gen Failed: {e}")
            explain_time = -1
        
        total_time = (gen_time if gen_time > 0 else 0) + exec_time + (explain_time if explain_time > 0 else 0)
        print(f"Total Math Time (Success parts): {total_time:.4f}s")
        
        return {
            "gen": gen_time,
            "exec": exec_time,
            "explain": explain_time,
            "total": total_time
        }
    except Exception as e:
        print(f"Math Benchmark Failed: {e}")
        return None

async def benchmark_web_search():
    print("\n--- Benchmarking WebSearchSkill ---")
    
    # Mock Session ID
    token = session_id_ctx.set("benchmark_session_id")
    
    try:
        skill = WebSearchSkill()
        # Reset limit for testing if needed, though session_id is new so it should be fine
        # Mock SessionManager.is_search_used to return False if possible, but here we use a new session
        
        query = "Latest developments in Quantum Computing 2024"
        print(f"Query: {query}")
        
        # 1. Measure Total Execution
        start = time.perf_counter()
        result = await skill.execute(query)
        total_time = time.perf_counter() - start
        print(f"[Total] Web Search Execution: {total_time:.4f}s")
        
        # Analyze breakdown if possible
        details = result.get("details", {})
        latency_reported = details.get("latency_ms", 0) / 1000.0
        print(f"[Reported] Internal Latency: {latency_reported:.4f}s")
        
        # 2. Measure Raw Search (if Tavily is used)
        if skill.engine == "tavily" and skill.search_tool:
            print("Benchmarking Raw Tavily API...")
            start = time.perf_counter()
            # Raw invoke
            await skill.search_tool.ainvoke({"query": query})
            raw_time = time.perf_counter() - start
            print(f"[Raw] Tavily API Call: {raw_time:.4f}s")
            print(f"[Overhead] Processing/Scraping: {total_time - raw_time:.4f}s")
        
        return {
            "total": total_time
        }
            
    except Exception as e:
        print(f"Web Search Benchmark Failed: {e}")
        return None

async def main():
    print("Starting Benchmarks...")
    print(f"DeepSeek Model: {getattr(settings, 'DEEPSEEK_MODEL', 'Not Set')}")
    
    math_results = await benchmark_math_solver()
    web_results = await benchmark_web_search()
    
    print("\n--- Diagnosis Summary ---")
    if math_results:
        # Check if code generation is the bottleneck
        if math_results["gen"] > 2.0:
            print("! Math: Code Generation is slow (>2s). Consider smaller model or prompt optimization.")
        # Check if execution is the bottleneck
        if math_results["exec"] > 1.0:
            print("! Math: Code Execution is slow (>1s). Sandbox startup might be the cause.")
        # Check if explanation is the bottleneck
        if math_results["explain"] > 2.0:
            print("! Math: Explanation Generation is slow (>2s). This step might be optional or streamable.")
            
    if web_results:
        pass

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
