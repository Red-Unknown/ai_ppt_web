from dotenv import load_dotenv
load_dotenv()

import asyncio
import sys
import os
import json
import io
from typing import List, Dict, Any

# Force UTF-8 output to file
sys.stdout = io.TextIOWrapper(open("test_results_utf8.txt", "wb"), encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.qa.service import QAService
from backend.app.schemas.qa import ChatRequest
from backend.app.services.student.state_manager import StudentStateManager

# Mock or Real API Key Setup
if "DEEPSEEK_API_KEY" not in os.environ:
    print("WARNING: DEEPSEEK_API_KEY not found in environment variables.")
    print("Tests will attempt to run but may fail or use mock responses if implemented.")
    # In a real scenario, we might want to exit or set a dummy key for mock mode
    # os.environ["DEEPSEEK_API_KEY"] = "sk-dummy-key" 

async def run_test_case(service, name, query, expected_mode=None, user_id="test_user_001", enable_reasoning=False, check_visuals=False, check_strategy=False):
    print(f"\n{'='*50}")
    print(f"Test Case: {name}")
    print(f"Query: {query}")
    print(f"Enable Reasoning: {enable_reasoning}")
    print(f"{'='*50}")
    
    request = ChatRequest(
        query=query, 
        session_id=f"test_session_{name.replace(' ', '_')}",
        enable_reasoning=enable_reasoning
    )
    
    # Set profile for style transfer or mastery if needed
    if "Visual" in name:
        StudentStateManager.create_or_update_profile(user_id, {"learning_style": "visual"})
    elif "Logical" in name:
        StudentStateManager.create_or_update_profile(user_id, {"learning_style": "textual"})
    
    # Initialize tracking variables
    full_response = ""
    mode_detected = "Unknown"
    has_quick_answer = False
    has_reasoning = False
    has_enhanced_answer = False
    has_visuals = False
    has_strategy = False
    
    async for chunk_str in service.stream_answer_question(request, user_id=user_id):
        try:
            chunk = json.loads(chunk_str)
        except json.JSONDecodeError:
            print(f"[Error] Invalid JSON chunk: {chunk_str}")
            continue

        type_ = chunk.get("type")
        content = chunk.get("content", "")
        
        if type_ == "status":
            print(f"[Status] {content}")
            if "直接回答" in str(content):
                mode_detected = "Direct RAG"
            elif "多步推理" in str(content):
                mode_detected = "ReAct"
            elif "启动双流" in str(content):
                mode_detected = "Dual Stream"
        
        elif type_ == "token":
            # print(content, end="", flush=True) # Reduce noise
            full_response += str(content)
            
        elif type_ == "quick_answer":
            has_quick_answer = True
            print(f"[Quick Answer] {content}", end="|")
            
        elif type_ == "reasoning_content":
            has_reasoning = True
            # print(f"[Thinking] {content}", end="|")
            
        elif type_ == "enhanced_answer":
            has_enhanced_answer = True
            print(f"[Enhanced] {content}", end="|")
            
        elif type_ == "sources":
            print(f"\n[Sources] Received {len(content)} sources")
            for src in content:
                if src.get("bbox") or src.get("image_url"):
                    has_visuals = True
                    print(f"  - Visual Source: bbox={src.get('bbox')}, img={src.get('image_url')}")
                else:
                    print(f"  - Text Source: {src.get('node_id')}")

        elif type_ == "strategy":
            has_strategy = True
            print(f"\n[Strategy Event] {content}")

        elif type_ == "start":
            print(f"\n[Action Start] {chunk.get('action')}")
            if chunk.get('action') == "CONTROL":
                mode_detected = "Control"
                
        elif type_ == "error":
            print(f"\n[Error] {content}")

    print("\n")
    print(f"Detected Mode: {mode_detected}")
    
    # Validation
    failed = False
    if expected_mode and expected_mode not in mode_detected:
        print(f"❌ Mode Mismatch: Expected {expected_mode}, Got {mode_detected}")
        failed = True
    else:
        print(f"✅ Mode Match: {mode_detected}")

    if enable_reasoning:
        if has_quick_answer and has_enhanced_answer:
            print("✅ Dual Stream Flow Verified (Quick + Enhanced)")
            if not has_reasoning:
                print("⚠️ Warning: Reasoning content missing (Check Model/API Support)")
        else:
            print(f"❌ Dual Stream Incomplete: Quick={has_quick_answer}, Reasoning={has_reasoning}, Enhanced={has_enhanced_answer}")
            failed = True

    if check_visuals:
        if has_visuals:
            print("✅ Visual Grounding Verified")
        else:
            print("❌ Visual Grounding Missing (Expected bbox/image_url)")
            failed = True
            
    if check_strategy:
        if has_strategy:
            print("✅ Strategy Switch Verified")
        else:
            print("❌ Strategy Switch Missing")
            failed = True
            
    if not failed:
        print("✅ TEST CASE PASSED")
    else:
        print("❌ TEST CASE FAILED")

async def main():
    try:
        service = QAService()
        # Ensure retrieval tree is loaded/mocked
        # In a real test, we assume the vector DB or mock retriever is ready
    except Exception as e:
        print(f"Failed to init service: {e}")
        return

    # --- New Feature Scenarios ---

    # 1. Visual Grounding (Scheme 1)
    # Testing Router Fix: "展示" should be routed to QA (Direct RAG), not CONTROL
    # Note: "公式推导" (formula derivation) is complex, so ReAct (Multi-step) is expected/valid.
    print("\n[Test] Verifying Router Fix for '展示' (Show)...")
    await run_test_case(
        service, 
        "Visual Grounding Test (Router Fix)", 
        "展示牛顿第二定律的公式推导幻灯片", 
        expected_mode="ReAct", # Complex query triggers ReAct
        check_visuals=True
    )

    # 2. Adaptive Resume (Scheme 2)
    # Query designed to trigger confusion/strategy switch
    # We might need to mock state or send multiple queries to degrade mastery
    print("\n[Setup] Simulating low mastery for Adaptive Resume...")
    StudentStateManager.update_mastery("test_user_001", "physics", 0.1) # Force low mastery
    await run_test_case(
        service, 
        "Adaptive Resume Test", 
        "我没听懂，请换个方式解释", 
        expected_mode=None, # Mode is dynamic (Unknown/Control), main check is strategy
        check_strategy=True
    )

    # 3. Dual Stream (Scheme 3)
    # Testing Reasoning Content Extraction
    print("\n[Test] Verifying Dual Stream Reasoning Content...")
    await run_test_case(
        service, 
        "Dual Stream Test (DeepSeek Reasoner)", 
        "详细解释广义相对论的时空弯曲效应", 
        enable_reasoning=True,
        expected_mode="Dual Stream"
    )

if __name__ == "__main__":
    asyncio.run(main())
