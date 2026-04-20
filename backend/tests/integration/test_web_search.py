import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.services.qa.tools.web_search import WebSearchSkill, _query_cache
from backend.app.core.context import session_id_ctx


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    _query_cache.clear()
    yield
    _query_cache.clear()


@pytest.mark.asyncio
async def test_web_search_tavily_api():
    """Test web search using Tavily API."""
    # Setup
    skill = WebSearchSkill()
    skill.tavily_api_key = "test_key"
    skill.engine = "tavily"

    # Mock Tavily API response
    mock_response = {
        "answer": "This is a test search result from Tavily.",
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "content": "Test content 1"
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/2",
                "content": "Test content 2"
            }
        ]
    }

    with patch.object(skill, '_call_tavily_search', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response

        # Set session context
        token = session_id_ctx.set("test_session")
        try:
            # Mock SessionManager to allow search
            with patch("backend.app.services.session.manager.SessionManager.try_acquire_search_quota", return_value=True):
                # Execute
                result = await skill.execute("test query", request_id="req_test")
        finally:
            session_id_ctx.reset(token)

        # Verify Status
        assert result["status"] == "success"

        # Verify Tavily API was called
        mock_call.assert_called_once()

        # Verify Result Content
        assert "test search result" in result["content"]

        # Verify Sources
        assert len(result["details"]["sources"]) == 2
        assert result["details"]["engine"] == "tavily"


@pytest.mark.asyncio
async def test_web_search_quota_exceeded():
    """Test web search when quota is exceeded."""
    skill = WebSearchSkill()
    skill.tavily_api_key = "test_key"
    skill.engine = "tavily"

    # Set session context
    token = session_id_ctx.set("test_session_quota")
    try:
        # Mock SessionManager to reject search (quota exceeded)
        with patch("backend.app.services.session.manager.SessionManager.try_acquire_search_quota", return_value=False):
            result = await skill.execute("test query quota", request_id="req_test")
    finally:
        session_id_ctx.reset(token)

    # Verify quota exceeded response
    assert result["status"] == "success"
    assert "quota" in result["content"].lower() or "exhausted" in result["content"].lower()
    assert result["details"]["type"] == "limit_exceeded"


@pytest.mark.asyncio
async def test_web_search_no_api_key():
    """Test web search when API key is not configured."""
    skill = WebSearchSkill()
    skill.tavily_api_key = None
    skill.engine = "none"

    # Set session context
    token = session_id_ctx.set("test_session_no_key")
    try:
        with patch("backend.app.services.session.manager.SessionManager.try_acquire_search_quota", return_value=True):
            result = await skill.execute("test query no key", request_id="req_test")
    finally:
        session_id_ctx.reset(token)

    # Verify not configured response
    assert result["status"] == "success"
    assert "not configured" in result["content"].lower()
    assert result["details"]["engine"] == "none"


@pytest.mark.asyncio
async def test_web_search_cache_hit():
    """Test web search cache functionality."""
    skill = WebSearchSkill()
    skill.tavily_api_key = "test_key"
    skill.engine = "tavily"

    # Pre-populate cache
    cached_result = {
        "status": "success",
        "content": "Cached result",
        "details": {
            "sources": [{"title": "Cached", "link": "", "snippet": "cached"}],
            "type": "web_search_results",
            "engine": "tavily"
        }
    }
    skill._save_to_cache("cached query", cached_result)

    # Set session context
    token = session_id_ctx.set("test_session_cache")
    try:
        result = await skill.execute("cached query", request_id="req_test")
    finally:
        session_id_ctx.reset(token)

    # Verify cache hit
    assert result["details"]["cache_hit"] is True
    assert result["content"] == "Cached result"


@pytest.mark.asyncio
async def test_web_search_api_error():
    """Test web search when Tavily API returns an error."""
    skill = WebSearchSkill()
    skill.tavily_api_key = "test_key"
    skill.engine = "tavily"

    with patch.object(skill, '_call_tavily_search', new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("API Error: Rate limit exceeded")

        # Set session context
        token = session_id_ctx.set("test_session_error")
        try:
            with patch("backend.app.services.session.manager.SessionManager.try_acquire_search_quota", return_value=True):
                result = await skill.execute("test query error", request_id="req_test")
        finally:
            session_id_ctx.reset(token)

        # Verify error handling
        assert result["status"] == "success"  # Returns success with error message
        assert "error" in result["content"].lower()
        assert result["details"]["status_code"] == 500
