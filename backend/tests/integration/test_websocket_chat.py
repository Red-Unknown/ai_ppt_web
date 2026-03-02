import os
import sys
import json
import pytest
from fastapi.testclient import TestClient
from typing import AsyncGenerator, List

# Set Mock API Key to pass Pydantic validation
os.environ["OPENAI_API_KEY"] = "sk-mock-key-for-testing"

# Add project root and backend to path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
# Import from 'app' directly because backend/main.py uses 'from app...'
# and we added backend directory to sys.path
from backend.app.api.v1.chat import get_qa_service
from backend.app.schemas.qa import ChatRequest

client = TestClient(app)

class MockQAService:
    async def predict_next_questions(self, query: str) -> List[str]:
        return ["Q1", "Q2", "Q3"]

    async def stream_answer_question(self, request: ChatRequest, user_id: str = "student_001") -> AsyncGenerator[str, None]:
        print(f"MockQAService called with query: {request.query}")
        # Simulate Cache Hit logic if query matches
        if request.query == "课程介绍":
            yield json.dumps({"type": "start", "action": "QA_CACHE"})
            yield json.dumps({"type": "token", "content": "本课程是《大学物理》..."})
            yield json.dumps({"type": "end"})
            return

        # Simulate Stream
        yield json.dumps({"type": "start", "action": "QA_ANSWER"})
        tokens = ["New", "ton", "'s", " Sec", "ond", " Law", " is", " F", "=", "ma"]
        for token in tokens:
            yield json.dumps({"type": "token", "content": token})
        yield json.dumps({"type": "end"})

    async def answer_question(self, request: ChatRequest, user_id: str = "student_001"):
        return {"content": "Mock Answer", "action": "QA_ANSWER"}

def test_websocket_chat_cache_hit():
    # Override dependency with Mock
    app.dependency_overrides[get_qa_service] = lambda: MockQAService()
    
    print("\n[Testing WebSocket] Cache Hit Scenario...")
    with client.websocket_connect("/api/v1/chat/ws") as websocket:
        # Send a cached query
        request_data = {
            "query": "课程介绍",
            "session_id": "test_ws_session",
            "current_path": "intro"
        }
        websocket.send_text(json.dumps(request_data))
        
        # Receive responses
        messages = []
        while True:
            try:
                # Receive with timeout to prevent hanging
                data = websocket.receive_text()
                msg = json.loads(data)
                messages.append(msg)
                print(f"Received: {msg}")
                if msg.get("type") == "end":
                    break
            except Exception as e:
                print(f"Error or Timeout: {e}")
                break
        
        # Assertions
        assert len(messages) >= 3
        assert messages[0]["type"] == "start"
        assert messages[0]["action"] == "QA_CACHE"
        assert messages[1]["type"] == "token"
        assert "本课程是《大学物理》" in messages[1]["content"]
        assert messages[-1]["type"] == "end"
        print("[SUCCESS] Cache Hit Test Passed")

def test_websocket_chat_qa_stream():
    # Override dependency with Mock
    app.dependency_overrides[get_qa_service] = lambda: MockQAService()
    
    print("\n[Testing WebSocket] QA Stream Scenario...")
    with client.websocket_connect("/api/v1/chat/ws") as websocket:
        request_data = {
            "query": "What is Newton's Second Law?",
            "session_id": "test_ws_session_qa",
            "current_path": "mechanics"
        }
        websocket.send_text(json.dumps(request_data))
        
        messages = []
        has_token = False
        while True:
            data = websocket.receive_text()
            msg = json.loads(data)
            messages.append(msg)
            print(f"Received msg in QA stream: {msg}")
            
            if msg.get("type") == "token":
                has_token = True
                sys.stdout.write(msg["content"])
                sys.stdout.flush()
            
            if msg.get("type") == "end":
                break
                
        assert has_token
        print("\n[SUCCESS] QA Stream Test Passed")

def test_websocket_edge_filter():
    # Override dependency with Mock
    app.dependency_overrides[get_qa_service] = lambda: MockQAService()
    
    print("\n[Testing WebSocket] Edge Filter Scenario...")
    with client.websocket_connect("/api/v1/chat/ws") as websocket:
        request_data = {
            "query": "This is a sql injection attack",
            "session_id": "test_ws_security",
            "current_path": "security"
        }
        websocket.send_text(json.dumps(request_data))
        
        # Expect error message
        data = websocket.receive_text()
        msg = json.loads(data)
        print(f"Received: {msg}")
        
        assert msg["type"] == "error"
        assert "Malicious content detected" in msg["content"]
        print("[SUCCESS] Edge Filter Test Passed")

if __name__ == "__main__":
    test_websocket_chat_cache_hit()
    test_websocket_chat_qa_stream()
    test_websocket_edge_filter()
