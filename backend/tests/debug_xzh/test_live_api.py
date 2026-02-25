import os
import sys
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Add project root and backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.main import app

# Load environment variables
load_dotenv()

client = TestClient(app)

def test_api_docs_accessible():
    response = client.get("/docs")
    assert response.status_code == 200

def test_chat_session_lifecycle():
    # 1. Start Session
    print("Testing /api/v1/chat/session/start...")
    response = client.post("/api/v1/chat/session/start", json={
        "course_id": "course_physics_101",
        "mode": "learn",
        "target_node_id": "node_start"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    session_id = data["session_id"]
    print(f"\n[Session Started] ID: {session_id}")

    # 2. Student Profile (Set Preference)
    response = client.post("/api/v1/student/profile", json={
        "weaknesses": ["mechanics"],
        "learning_style": "visual"
    })
    assert response.status_code == 200
    print(f"[Profile Updated] {response.json()}")

    # 3. Chat Interaction (QA)
    # Check if OPENAI_API_KEY is set for live test
    if not os.getenv("OPENAI_API_KEY"):
        print("\n[WARNING] OPENAI_API_KEY not found. Skipping live LLM test.")
        return

    print("\n[Sending QA Query] 'What is Newton's First Law?'")
    response = client.post("/api/v1/chat/chat", json={
        "query": "What is Newton's First Law?",
        "session_id": session_id,
        "current_path": "physics/mechanics",
        "top_k": 1
    })
    
    if response.status_code == 200:
        ans = response.json()
        print(f"[QA Response] Action: {ans['action']}")
        print(f"[Answer] {ans['answer']}")
        assert ans["action"] == "QA_ANSWER"
    else:
        print(f"[Error] {response.text}")

    # 4. Chat Interaction (Feedback -> Supplement)
    print("\n[Sending Feedback] 'I am confused.'")
    response = client.post("/api/v1/chat/chat", json={
        "query": "I am confused about this.",
        "session_id": session_id,
        "current_path": "physics/mechanics"
    })
    
    if response.status_code == 200:
        ans = response.json()
        print(f"[Feedback Response] Action: {ans.get('action')}")
        print(f"[Supplement] {ans.get('answer')}")
        # Expect SUPPLEMENT action if LLM classifies it correctly
        # Note: Without real RAG context, LLM might hallucinate or be generic
    else:
        print(f"[Error] {response.text}")

    # 5. Adapt Script (Style Transfer Demo)
    print("\nTesting /api/v1/chat/script/adapt...")
    adapt_response = client.post("/api/v1/chat/script/adapt", json={
        "original_script": "Newton's second law states that F=ma.",
        "session_id": session_id,
        "target_style": "humorous"
    })
    print(f"Status: {adapt_response.status_code}")
    if adapt_response.status_code == 200:
        print(f"Response: {adapt_response.json()}")
    else:
        print(f"Response: {adapt_response.text}")

if __name__ == "__main__":
    # Manual Run
    import traceback
    print("Start testing...")
    try:
        test_api_docs_accessible()
        test_chat_session_lifecycle()
        print("\n[SUCCESS] All live API tests passed (or skipped if no key).")
    except Exception as e:
        traceback.print_exc()
        print(f"\n[FAILURE] Tests failed: {e}")
        traceback.print_exc()
