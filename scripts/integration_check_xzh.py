import os
import sys
import json
from contextlib import contextmanager

# Ensure import paths
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "backend"))

from fastapi.testclient import TestClient
from backend.main import app
from app.api.v1.chat import get_qa_service
from backend.app.schemas.qa import ChatRequest
from typing import AsyncGenerator, List

class MockQAService:
    def reload_config(self):
        return True
    async def predict_next_questions(self, query: str) -> List[str]:
        return ["Q1", "Q2", "Q3"]

    async def stream_answer_question(self, request: ChatRequest, user_id: str = "student_001") -> AsyncGenerator[str, None]:
        if request.query == "课程介绍":
            yield json.dumps({"type": "start", "action": "QA_CACHE"})
            yield json.dumps({"type": "token", "content": "本课程是《大学物理》..."})
            yield json.dumps({"type": "suggestions", "content": ["Q1","Q2","Q3"]})
            yield json.dumps({"type": "end"})
            return
        yield json.dumps({"type": "start", "action": "QA_ANSWER"})
        for t in ["A","n","s","w","e","r"]:
            yield json.dumps({"type": "token", "content": t})
        yield json.dumps({"type": "end"})

@contextmanager
def override_dependencies():
    app.dependency_overrides[get_qa_service] = lambda: MockQAService()
    try:
        yield
    finally:
        app.dependency_overrides.clear()

def main():
    os.environ.setdefault("DEEPSEEK_API_KEY", "sk-mock-key")
    client = TestClient(app)

    with override_dependencies():
        # Reload
        r = client.post("/api/v1/chat/config/reload")
        assert r.status_code == 200

        # WS cache path
        with client.websocket_connect("/api/v1/chat/ws") as ws:
            ws.send_text(json.dumps({"query":"课程介绍","session_id":"s1","current_path":"intro"}))
            msgs = []
            while True:
                data = ws.receive_text()
                m = json.loads(data)
                msgs.append(m)
                if m.get("type") == "end":
                    break
        actions = [m.get("action") for m in msgs if m.get("type") == "start"]
        assert "QA_CACHE" in actions

    print("Integration check (xzh) OK")

if __name__ == "__main__":
    main()
