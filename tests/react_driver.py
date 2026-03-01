import asyncio
import time
import json
import os
import sys
import cProfile
import pstats
from typing import List, Dict, Any

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Check for real API keys
HAS_REAL_KEYS = bool(os.environ.get("DEEPSEEK_API_KEY")) and not os.environ.get("DEEPSEEK_API_KEY").startswith("sk-your")

if not HAS_REAL_KEYS:
    print("⚠️ No real API keys found. Falling back to Mock Mode.")
    from unittest.mock import MagicMock, patch
    from langchain_core.messages import AIMessage
    
    # Mock dependencies
    sys.modules["html2text"] = MagicMock()
    
    # Mock ChatOpenAI globally for the driver
    patcher = patch('langchain_openai.ChatOpenAI')
    MockChatOpenAI = patcher.start()
    mock_llm_instance = MockChatOpenAI.return_value
    
    async def mock_ainvoke(input, **kwargs):
        # Basic ReAct Mock Response
        messages = input
        
        # Heuristic: If input is a list of BaseMessages (ReAct), treat as Agent
        is_react_call = isinstance(input, list) and len(input) > 0 and hasattr(input[0], 'type')
        
        if is_react_call:
            has_observation = any("ToolMessage" in str(type(m)) for m in messages)
            
            if has_observation:
                return AIMessage(content="Final Answer: The result is 42.")
            else:
                return AIMessage(
                    content="Thinking: I should use a tool.",
                    tool_calls=[{
                        "name": "math_solver",
                        "args": {"query": "Calculate 2+2"},
                        "id": "call_123"
                    }]
                )
        else:
            return AIMessage(content="import math\nresult = 42")
    
    def mock_invoke(input, **kwargs):
        return AIMessage(content="import math\nresult = 42")
    
    mock_llm_instance.ainvoke.side_effect = mock_ainvoke
    mock_llm_instance.invoke.side_effect = mock_invoke
    mock_llm_instance.bind_tools.return_value = mock_llm_instance
else:
    print("✅ Real API Keys found. Running with Live LLM.")
    # Ensure dependencies
    try:
        import html2text
    except ImportError:
        pass # WebSearchSkill handles this

from backend.app.services.qa.agents.react import ReActAgent
from backend.app.services.qa.tools.calculator import MathSkill
from backend.app.services.qa.tools.web_search import WebSearchSkill
from backend.app.services.qa.tools.retrieval import LocalKnowledgeTool
from backend.app.services.qa.retrieval.tree_retriever import TreeStructureRetriever
from backend.app.core.config import settings
from langchain_openai import ChatOpenAI

# 10 Standard Tasks
TASKS = [
    "Calculate the square root of 256 plus 10.", 
    "Search for the latest Python version.", 
    "Compare Newton's First Law and Third Law.", 
    "Who is the current president of France?", 
    "Find the definition of 'Recursion'.", 
    "If I have 5 apples and eat 2, how many do I have?", 
    "What is the weather in Tokyo?", 
    "Explain the difference between List and Tuple.", 
    "Solve 3x + 5 = 20.", 
    "Summarize the course grading policy." 
]

async def run_react_task(agent: ReActAgent, task: str) -> Dict[str, Any]:
    start_time = time.time()
    steps = 0
    trajectory = []
    success = False
    
    try:
        async for event_str in agent.run(task):
            event = json.loads(event_str)
            evt_type = event.get("type")
            
            if evt_type == "thought":
                trajectory.append(f"Thought: {event.get('content')}")
            elif evt_type == "tool_start":
                steps += 1
                trajectory.append(f"Action: {event.get('tool')} ({event.get('input')})")
            elif evt_type == "tool_end":
                trajectory.append(f"Observation: {event.get('output')}")
            elif evt_type == "answer":
                trajectory.append(f"Answer: {event.get('content')}")
                success = True
            elif evt_type == "done":
                pass
                
    except Exception as e:
        trajectory.append(f"Error: {e}")
        success = False
        
    duration = time.time() - start_time
    
    return {
        "task": task,
        "success": success,
        "steps": steps,
        "duration": duration,
        "trajectory": trajectory
    }

async def main():
    print("Initializing ReAct Driver...")
    
    retriever = TreeStructureRetriever()
    
    if HAS_REAL_KEYS:
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
            temperature=0
        )
    else:
        llm = mock_llm_instance
    
    # Initialize Tools
    tools = [
        MathSkill(llm_model="deepseek-chat" if HAS_REAL_KEYS else "gpt-3.5-turbo"),
        WebSearchSkill(),
        LocalKnowledgeTool(retriever=retriever, llm=llm)
    ]
    
    agent = ReActAgent(llm=llm, tools=tools, max_iterations=5 if HAS_REAL_KEYS else 3)
    
    results = []
    
    print(f"Starting Benchmark on {len(TASKS)} tasks...")
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    for i, task in enumerate(TASKS):
        print(f"Running Task {i+1}: {task}")
        result = await run_react_task(agent, task)
        results.append(result)
        print(f"  -> Success: {result['success']}, Steps: {result['steps']}, Time: {result['duration']:.2f}s")
        
    profiler.disable()
    profiler.dump_stats("react_benchmark.prof")
    
    generate_report(results)

def generate_report(results: List[Dict[str, Any]]):
    total = len(results)
    success_count = sum(1 for r in results if r["success"])
    avg_steps = sum(r["steps"] for r in results) / total if total else 0
    avg_time = sum(r["duration"] for r in results) / total if total else 0
    
    report_content = f"""# ReAct Benchmark Report

## Summary
- **Total Tasks**: {total}
- **Success Rate**: {success_count/total*100:.1f}%
- **Average Steps**: {avg_steps:.2f}
- **Average Duration**: {avg_time:.2f}s

## Detailed Results

| Task | Success | Steps | Duration (s) |
| :--- | :---: | :---: | :---: |
"""
    
    for r in results:
        report_content += f"| {r['task']} | {'✅' if r['success'] else '❌'} | {r['steps']} | {r['duration']:.2f} |\n"
        
    report_content += "\n## Trajectories\n\n"
    for i, r in enumerate(results):
        report_content += f"### Task {i+1}: {r['task']}\n"
        for line in r['trajectory']:
            report_content += f"- {line}\n"
        report_content += "\n"
        
    with open("react_benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("Benchmark Report generated: react_benchmark_report.md")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
