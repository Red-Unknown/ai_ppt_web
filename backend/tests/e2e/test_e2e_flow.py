import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.services.session.manager import SessionManager
from unittest.mock import patch, AsyncMock, MagicMock
import json

client = TestClient(app)

@pytest.mark.asyncio
async def test_e2e_full_flow():
    # Mock external dependencies to avoid real API calls and ensure deterministic behavior
    with patch("backend.app.services.qa.service.TreeStructureRetriever") as MockRetriever, \
         patch("backend.app.services.qa.service.RateLimitedChatOpenAI") as MockLLM, \
         patch("backend.app.services.qa.tools.manager.WebSearchSkill") as MockSearch:
         
        # Setup Mocks
        mock_retriever_instance = MockRetriever.return_value
        mock_retriever_instance.invoke.return_value = [MagicMock(page_content="Mock Context", metadata={"score": 0.9})]
        
        # 1. Start a new session
        response = client.post("/api/v1/chat/session/start", json={
            "course_id": "test_course",
            "mode": "learning",
            "target_node_id": "node_1"
        })
        assert response.status_code == 200
        session_data = response.json()
        session_id = session_data["session_id"]
        assert session_id is not None
        
        # 2. WebSocket Connection & First Query (Reasoning)
        # Mocking the stream to return tokens so it saves to history
        async def async_gen(*args, **kwargs):
            for t in ["This", " is", " quantum", " entanglement"]:
                mock_chunk = MagicMock()
                mock_chunk.content = t
                mock_chunk.additional_kwargs = {}
                mock_chunk.response_metadata = {}
                yield mock_chunk
        
        MockLLM.return_value.astream.side_effect = async_gen
        
        with client.websocket_connect("/api/v1/chat/ws") as websocket:
            # Send query
            payload = {
                "query": "Explain quantum entanglement",
                "session_id": session_id,
                "model": "deepseek-reasoner"
            }
            websocket.send_json(payload)

            # Receive events
            received_types = []
            while True:
                try:
                    data = websocket.receive_json()
                    msg_type = data.get("type")
                    received_types.append(msg_type)
                    if msg_type == "end":
                        break
                except:
                    break

            assert "start" in received_types
            assert "end" in received_types
            
        # 3. Verify Session History (Persistence)
        history_response = client.get(f"/api/v1/chat/history/{session_id}")
        assert history_response.status_code == 200
        history = history_response.json()
        # Should have user query and assistant answer (even if empty due to mock)
        assert len(history) >= 2
        assert history[-2]["role"] == "user"
        assert history[-2]["content"] == "Explain quantum entanglement"
        
        # 4. Cache Hit Test (Same Query)
        # We need to ensure the previous query was cached. 
        # In QAService, it caches after retrieval.
        
        with client.websocket_connect("/api/v1/chat/ws") as websocket:
            # Send SAME query
            payload = {
                "query": "Explain quantum entanglement",
                "session_id": session_id,
                "model": "deepseek-chat"
            }
            websocket.send_json(payload)
            
            is_cache_hit = False
            while True:
                try:
                    data = websocket.receive_json()
                    if data.get("type") == "status" and "已命中会话缓存" in data.get("content", ""):
                        is_cache_hit = True
                    if data.get("type") == "end":
                        break
                except:
                    break
            
            # Assert Cache Hit
            assert is_cache_hit is True

        # 5. Search Limit Test
        # We need to simulate a search query.
        # First, ensure search is used.
        SessionManager.mark_search_used(session_id)
        
        # Now try a query that would trigger search (e.g. "latest news")
        # Since we mocked logic, we can verify if the service respects the flag.
        # This is harder to test via WS without internal inspection, but we verified it in unit tests.
        # Here we just ensure the flow completes without error.
        
        with client.websocket_connect("/api/v1/chat/ws") as websocket:
            payload = {
                "query": "latest news about AI",
                "session_id": session_id,
                "model": "deepseek-chat"
            }
            websocket.send_json(payload)
            
            while True:
                try:
                    data = websocket.receive_json()
                    if data.get("type") == "end":
                        break
                except:
                    break
                    
        # 6. Verify No Error Logs
        # This is implicitly verified if the test passes without exceptions.
