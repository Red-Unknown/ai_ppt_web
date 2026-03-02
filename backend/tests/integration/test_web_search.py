import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.services.qa.tools.web_search import WebSearchSkill
from backend.app.core.context import session_id_ctx

@pytest.mark.asyncio
async def test_web_search_parallel_execution():
    # Setup
    skill = WebSearchSkill()
    skill.search_tool = AsyncMock()
    skill.engine = "tavily"
    
    # Mock search results (Top 5)
    mock_results = [
        {"url": f"http://test{i}.com", "content": f"snippet{i}"}
        for i in range(1, 6)
    ]
    skill.search_tool.ainvoke.return_value = mock_results
    
    # Mock scrape content
    with patch.object(skill, '_scrape_content', new_callable=AsyncMock) as mock_scrape:
        mock_scrape.side_effect = [f"full_content_{i}" for i in range(1, 6)]
        
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
        
        # Verify Search Tool Called
        skill.search_tool.ainvoke.assert_called_once()
        
        # Verify Parallel Scraping (Should be called 5 times)
        assert mock_scrape.call_count == 5
        
        # Verify Result Content contains scraped content indicator
        assert "Full Content Available" in result["content"]

@pytest.mark.asyncio
async def test_web_search_timeout():
    # Setup
    skill = WebSearchSkill()
    skill.search_tool = AsyncMock()
    skill.engine = "tavily"
    
    # Mock search results
    skill.search_tool.ainvoke.return_value = [{"url": "http://slow.com", "content": "slow"}]
    
    # Mock scrape content to hang
    async def slow_scrape(*args, **kwargs):
        await asyncio.sleep(5) # Longer than 3s timeout
        return "slow content"
        
    with patch.object(skill, '_scrape_content', side_effect=slow_scrape):
        # Set session context
        token = session_id_ctx.set("test_session")
        try:
            # Mock SessionManager to allow search
            with patch("backend.app.services.session.manager.SessionManager.try_acquire_search_quota", return_value=True):
                # Execute
                result = await skill.execute("test query", request_id="req_timeout")
        finally:
            session_id_ctx.reset(token)
        
        # Should still return success (partial results)
        assert result["status"] == "success"
        
        # Check logs/process steps for timeout message
        process_steps = result["details"]["process"]
        assert any("timed out" in step for step in process_steps)
