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
        yield json.dumps({"type": "start", "action": "QA_CACHE"})
        yield json.dumps({"type": "token", "content": "SSE Content"})
        
        suggestions = await self.predict_next_questions(request.query)
        yield json.dumps({"type": "suggestions", "content": suggestions})
        
        yield json.dumps({"type": "end"})
    
    async def answer_question(self, request: ChatRequest, user_id: str = "student_001"):
        return {"content": "Mock Answer", "action": "QA_ANSWER"}

    async def adapt_script(self, request, user_id="student_001"):
        return {}

def test_sse_endpoint():
    # Override dependency
    app.dependency_overrides[get_qa_service] = lambda: MockQAService()
    
    print("\n[Testing SSE] Streaming...")
    # Using GET for SSE as implemented
    response = client.get("/api/v1/chat/sse?query=TestSSE")
    
    assert response.status_code == 200
    # Note: starlette/fastapi might add charset, so check 'startswith' or 'in'
    assert "text/event-stream" in response.headers["content-type"]
    
    content = ""
    for line in response.iter_lines():
        if line:
            print(f"Line: {line}")
            content += line
            
    if not content:
        content = response.text
        print(f"Full text: {content}")

    assert "data:" in content or "data: " in response.text
    assert "SSE Content" in content or "SSE Content" in response.text
    assert "suggestions" in content or "suggestions" in response.text
    
    print("[SUCCESS] SSE Test Passed")

if __name__ == "__main__":
    test_sse_endpoint()
