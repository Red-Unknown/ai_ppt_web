
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from backend.app.services.qa.tools.web_search import WebSearchSkill
from backend.app.core.context import session_id_ctx

# Mock settings to avoid missing API key errors during initialization
with patch("backend.app.core.config.settings") as mock_settings:
    mock_settings.TAVILY_API_KEY = "mock_key"
    mock_settings.DEEPSEEK_API_KEY = "mock_key"

@pytest.fixture
def web_search_skill():
    with patch("backend.app.services.qa.tools.web_search.TavilySearchResults") as MockTavily:
        # Setup mock return for Tavily
        mock_tool = MagicMock()
        # ainvoke should be an async method
        mock_tool.ainvoke = AsyncMock(return_value=[
            {"url": "http://example.com/1", "content": "Content 1"},
            {"url": "http://example.com/2", "content": "Content 2"}
        ])
        MockTavily.return_value = mock_tool
        
        skill = WebSearchSkill()
        # Force engine to tavily for predictable behavior
        skill.engine = "tavily"
        skill.search_tool = mock_tool
        
        # Mock _scrape_content to avoid real network calls
        skill._scrape_content = AsyncMock(return_value="Mock Scraped Content")
        
        return skill

@pytest.fixture
def clean_session():
    # Use patch.dict to clear and set _CHAT_SESSIONS in the module
    session_id = "test_session_123"
    initial_data = {
        session_id: {
            "history": [],
            "search_used": False,
            "id": session_id,
            "user_id": "test_user"
        }
    }
    with patch("backend.app.services.session.manager._CHAT_SESSIONS", initial_data):
        yield session_id

@pytest.mark.asyncio
async def test_first_search_success(web_search_skill, clean_session):
    """
    Scenario 1: First search success.
    Verify:
    - Search proceeds (tool is called).
    - Session quota is marked as used.
    """
    session_id = clean_session
    token = session_id_ctx.set(session_id)
    
    try:
        from backend.app.services.session.manager import _CHAT_SESSIONS
        assert _CHAT_SESSIONS[session_id]["search_used"] is False
        
        # 2. Execute search
        result = await web_search_skill.execute("test query", request_id="req1")
        
        # 3. Verify result
        assert result["status"] == "success"
        assert "Found 2 results" in result["content"]
        
        # 4. Verify tool was called
        web_search_skill.search_tool.ainvoke.assert_called_once()
        
        # 5. Verify quota is consumed
        assert _CHAT_SESSIONS[session_id]["search_used"] is True
        
    finally:
        session_id_ctx.reset(token)

@pytest.mark.asyncio
async def test_first_search_failure_counts_as_used(web_search_skill, clean_session):
    """
    Scenario 2: First search failure.
    Verify:
    - Search is attempted but fails (e.g., network error).
    - Session quota is STILL marked as used (strict 1 attempt).
    """
    session_id = clean_session
    token = session_id_ctx.set(session_id)
    
    # Simulate tool failure
    web_search_skill.search_tool.ainvoke.side_effect = Exception("Network Error")
    
    try:
        # 1. Execute search
        result = await web_search_skill.execute("test query", request_id="req2")
        
        # 2. Verify quota is consumed
        from backend.app.services.session.manager import _CHAT_SESSIONS
        assert _CHAT_SESSIONS[session_id]["search_used"] is True
        
    finally:
        session_id_ctx.reset(token)

@pytest.mark.asyncio
async def test_second_search_blocked(web_search_skill, clean_session):
    """
    Scenario 3: Attempt second search blocked.
    Verify:
    - Search is blocked immediately.
    - Tool is NOT called.
    - Returns specific warning/instruction.
    """
    session_id = clean_session
    token = session_id_ctx.set(session_id)
    
    from backend.app.services.session.manager import _CHAT_SESSIONS
    # Manually set search as used
    _CHAT_SESSIONS[session_id]["search_used"] = True
    
    try:
        # 1. Execute search
        result = await web_search_skill.execute("second query", request_id="req3")
        
        # 2. Verify result is error/limit reached
        assert result["status"] == "success" # Changed from error to success to stop retry
        assert "Search limit reached" in result["content"] or "exhausted" in result["content"]
        assert "如需更详细的内容请继续讨论" in result["content"]
        
        # 3. Verify tool was NOT called
        web_search_skill.search_tool.ainvoke.assert_not_called()
        
    finally:
        session_id_ctx.reset(token)

@pytest.mark.asyncio
async def test_parallel_search_execution(web_search_skill, clean_session):
    """
    Scenario 4: Verify parallel search logic (integration check).
    We can't easily check parallelism without adding delays in the mock,
    but we can check that _scrape_content is called multiple times for one execute.
    """
    session_id = clean_session
    token = session_id_ctx.set(session_id)
    
    # Ensure call count is reset if mocked in fixture
    web_search_skill._scrape_content.reset_mock()
    
    try:
        import time
        start_time = time.time()
        
        result = await web_search_skill.execute("test query", request_id="req4")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify scraping was called for each result (mock returns 2 results)
        assert web_search_skill._scrape_content.call_count == 2
        
        print(f"Search Duration: {duration:.4f}s") # For performance report
        
    finally:
        session_id_ctx.reset(token)
