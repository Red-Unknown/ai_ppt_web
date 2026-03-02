import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.app.services.qa.service import QAService
from backend.app.schemas.qa import ChatRequest, Intent
from backend.app.services.session.manager import SessionManager
import json

@pytest.mark.asyncio
async def test_qa_service_integration():
    # Patch dependencies to avoid real API calls
    with patch("backend.app.services.qa.service.TreeStructureRetriever"), \
         patch("backend.app.services.qa.service.LocalKnowledgeTool"), \
         patch("backend.app.services.qa.service.ReActAgent"), \
         patch("backend.app.services.qa.service.RateLimitedChatOpenAI"), \
         patch("backend.app.services.qa.service.DialogueRouter"), \
         patch("backend.app.services.qa.service.QAAnalyzer"): # Mock Analyzer
         
        service = QAService()
        service.retriever = MagicMock()
        service.retriever.invoke.return_value = []
        service.router = MagicMock()
        service.router.route.return_value = Intent.QA
        service.analyzer = MagicMock()
        service.analyzer.analyze = AsyncMock(return_value="FACTOID") # Default simple QA
        
        # --- Test 1: Cache Hit ---
        session_id = SessionManager.create_chat_session("u1")
        cached_docs = [MagicMock(page_content="cached content", metadata={"score": 0.9})]
        SessionManager.cache_docs(session_id, "cached query", cached_docs)
        
        # Verify cache is present
        # print(f"DEBUG: Session ID: {session_id}")
        # print(f"DEBUG: Cache: {SessionManager.get_cached_docs(session_id, 'cached query')}")
        
        request = ChatRequest(query="cached query", session_id=session_id)
        
        chunks = []
        async for chunk in service.stream_answer_question(request):
            chunks.append(chunk)
            # print(f"DEBUG: Chunk: {chunk}")
            
        # Verify cache hit message
        # Parse chunks to handle unicode escape
        messages = []
        for c in chunks:
            try:
                data = json.loads(c)
                if "content" in data:
                    messages.append(data["content"])
            except:
                pass
        
        assert any("已命中会话缓存" in m for m in messages)
        # Verify retriever NOT called (it was mocked above, call_count should be 0 for this query)
        service.retriever.invoke.assert_not_called()
        
        # --- Test 2: Search Limit ---
        # Since QAService resets search quota per turn, we must force is_search_used=True 
        # to verify the tool filtering logic (which handles the case where quota is exhausted).
        with patch("backend.app.services.qa.service.SessionManager.is_search_used", return_value=True):
            session_id_limit = SessionManager.create_chat_session("u2")
            # SessionManager.mark_search_used(session_id_limit) # No longer needed due to mock

            request_limit = ChatRequest(query="search something", session_id=session_id_limit)

            # Mock Agent
            service.agent = MagicMock()
            web_tool = MagicMock()
            web_tool.name = "web_search"
            other_tool = MagicMock()
            other_tool.name = "calculator"
            service.agent.tools = [web_tool, other_tool]

            # Capture tools during run
            captured_tools = []

            async def mock_run(*args, **kwargs):     
                # Capture the tools set on the agent at this moment
                # print(f"DEBUG: Mock Run Called. Tools: {[t.name for t in service.agent.tools]}")        
                captured_tools.extend(service.agent.tools)
                yield json.dumps({"type": "done"})   

            service.agent.run = mock_run

            # Force ReAct path
            service.analyzer.analyze = AsyncMock(return_value="MATH_CALCULATION") # Triggers ReAct        

            async for chunk in service.stream_answer_question(request_limit):
                pass
                # print(f"DEBUG: Limit Chunk: {chunk}")

            # Verify web_search was removed
            # print(f"DEBUG: Captured Tools: {captured_tools}")
            tool_names = [t.name for t in captured_tools]
            assert "web_search" not in tool_names
            assert "calculator" in tool_names
        
        # Verify tools restored
        restored_names = [t.name for t in service.agent.tools]
        assert "web_search" in restored_names
