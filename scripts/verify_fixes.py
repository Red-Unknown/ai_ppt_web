import sys
import os
import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock, patch
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set dummy env vars before importing app modules
os.environ["DEEPSEEK_API_KEY"] = "sk-dummy-key"
os.environ["TAVILY_API_KEY"] = "tv-dummy-key"

from backend.app.services.qa.service import QAService
from backend.app.schemas.qa import ChatRequest
from backend.app.services.session.manager import SessionManager, _CHAT_SESSIONS
from backend.app.core.context import AppContext, session_id_ctx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("verify_fixes")

async def test_search_quota_reset():
    logger.info(">>> Testing Search Quota Reset (Single Session Logic)...")
    
    session_id = "test_session_quota_1"
    user_id = "test_user_1"
    
    # Initialize a mock session
    SessionManager.create_chat_session(user_id)
    _CHAT_SESSIONS[session_id] = {
        "id": session_id,
        "user_id": user_id,
        "search_used": False,
        "history": [],
        "updated_at": "now"
    }
    
    # 1. Simulate quota consumption
    SessionManager.mark_search_used(session_id)
    assert SessionManager.is_search_used(session_id) == True, "Search should be used"
    logger.info("   Quota marked as used.")
    
    # 2. Simulate QAService turn start (which should reset quota)
    SessionManager.reset_search_quota(session_id)
    assert SessionManager.is_search_used(session_id) == False, "Search quota should be reset"
    logger.info("   Quota reset successfully.")
    
    logger.info("✅ Search Quota Reset Passed")

async def test_context_propagation():
    logger.info(">>> Testing Context Propagation...")
    
    session_id = "test_ctx_session"
    user_id = "test_ctx_user"
    
    with patch("backend.app.services.qa.service.TreeStructureRetriever"), \
         patch("backend.app.services.qa.service.DialogueRouter"), \
         patch("backend.app.services.qa.service.QAAnalyzer"), \
         patch("backend.app.services.qa.service.SkillManager"), \
         patch("backend.app.services.qa.service.TeacherAgent"), \
         patch("backend.app.services.qa.service.RateLimitedChatOpenAI"), \
         patch("backend.app.services.qa.service.ChatOpenAI"), \
         patch("backend.app.services.qa.service.LocalKnowledgeTool"), \
         patch("backend.app.services.qa.service.ReActAgent"), \
         patch("backend.app.services.qa.service.StudentStateManager"):
         
        service = QAService()
        service.intent_cache = {"test_query": "cached_answer"}
        
        request = ChatRequest(query="test_query", session_id=session_id)
        
        # Verify AppContext works independently
        with AppContext.scope(session_id=session_id, user_id=user_id):
            current_session = session_id_ctx.get()
            assert current_session == session_id, f"Context session_id mismatch: {current_session}"
            logger.info(f"   Inside scope: session_id={current_session}")
            
        current_session_after = session_id_ctx.get()
        assert current_session_after is None, "Context should be cleared after scope"
        logger.info("   Context cleared successfully.")
        
        # Verify QAService uses it via spy
        with patch("backend.app.core.context.AppContext.scope", wraps=AppContext.scope) as mock_scope:
            async for _ in service.stream_answer_question(request, user_id=user_id):
                pass
            
            mock_scope.assert_called()
            call_args = mock_scope.call_args
            assert call_args.kwargs['session_id'] == session_id
            assert call_args.kwargs['user_id'] == user_id
            logger.info("✅ QAService calls AppContext.scope Correctly")

async def test_streaming_react_mock():
    logger.info(">>> Testing ReAct Streaming Logic Check...")
    
    session_id = "test_react_session"
    user_id = "test_react_user"
    
    with patch("backend.app.services.qa.service.TreeStructureRetriever") as MockRetriever, \
         patch("backend.app.services.qa.service.DialogueRouter") as MockRouter, \
         patch("backend.app.services.qa.service.QAAnalyzer") as MockAnalyzer, \
         patch("backend.app.services.qa.service.SkillManager"), \
         patch("backend.app.services.qa.service.TeacherAgent"), \
         patch("backend.app.services.qa.service.RateLimitedChatOpenAI"), \
         patch("backend.app.services.qa.service.ChatOpenAI"), \
         patch("backend.app.services.qa.service.LocalKnowledgeTool"), \
         patch("backend.app.services.qa.service.ReActAgent") as MockAgentClass, \
         patch("backend.app.services.qa.service.StudentStateManager") as MockStateManager:
        
        service = QAService()
        service.intent_cache = {} 
        
        # Mock Router -> QA
        from backend.app.schemas.qa import Intent
        MockRouter.return_value.route.return_value = Intent.QA
        
        # Mock Analyzer -> MATH_CALCULATION (Complex intent)
        MockAnalyzer.return_value.analyze = AsyncMock(return_value="MATH_CALCULATION")
        
        # Mock Retriever -> Docs with score
        mock_doc = MagicMock()
        mock_doc.page_content = "Mock Context"
        mock_doc.metadata = {"score": 0.9, "path": "mock/path"}
        MockRetriever.return_value.invoke.return_value = [mock_doc]
        
        # Mock StateManager
        MockStateManager.get_history.return_value = []
        MockStateManager.get_profile.return_value = {}
        MockStateManager.get_state.return_value = MagicMock()
        
        # Mock Agent
        mock_agent_instance = MockAgentClass.return_value
        async def mock_agent_run(*args, **kwargs):
            yield '{"type": "thought_stream", "content": "Thinking..."}'
            yield '{"type": "thought_stream", "content": " Done."}'
            yield '{"type": "done"}'
            
        mock_agent_instance.run = mock_agent_run
        
        request = ChatRequest(query="Calculate 1+1", session_id=session_id)
        
        logger.info("   Invoking QAService with ReAct intent...")
        chunks = []
        async for chunk in service.stream_answer_question(request, user_id=user_id):
            chunks.append(chunk)
            
        # Debug output if failed
        if not any("Thinking" in c for c in chunks):
             logger.error(f"Captured chunks: {chunks}")

        thought_content = "".join([
            json.loads(c)["content"] 
            for c in chunks 
            if json.loads(c).get("type") == "token" and "Thinking" in json.loads(c).get("content", "")
        ])
        
        assert "Thinking..." in thought_content or "Thinking" in str(chunks), "Should verify thought stream content"
        logger.info("✅ ReAct Streaming Flow Verified")

async def main():
    try:
        await test_search_quota_reset()
        await test_context_propagation()
        await test_streaming_react_mock()
        logger.info("ALL TESTS PASSED")
    except Exception as e:
        logger.error(f"Test Failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
