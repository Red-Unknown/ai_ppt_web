import sys
import os
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock settings before importing analyzer
with patch('backend.app.core.config.settings') as mock_settings:
    mock_settings.DEEPSEEK_API_KEY = "mock_key"
    mock_settings.DEEPSEEK_BASE_URL = "http://mock"
    mock_settings.DEEPSEEK_MODEL = "deepseek-chat"
    
    from backend.app.services.qa.analyzer import QAAnalyzer

@pytest.mark.asyncio
async def test_analyzer_classification():
    # Mock ChatOpenAI
    with patch('backend.app.services.qa.analyzer.ChatOpenAI') as MockLLM:
        analyzer = QAAnalyzer()
        # Mock the chain
        analyzer.chain = AsyncMock()
        analyzer.chain.ainvoke.return_value = "MULTI_STEP"
        
        result = await analyzer.analyze("How to use quadratic functions to solve optimization problems?")
        assert result == "MULTI_STEP"
        
        analyzer.chain.ainvoke.return_value = "COMPARISON"
        result = await analyzer.analyze("Compare A and B")
        assert result == "COMPARISON"
        
        analyzer.chain.ainvoke.return_value = "EXAMPLE"
        result = await analyzer.analyze("Give me an example")
        assert result == "EXAMPLE"

@pytest.mark.asyncio
async def test_analyzer_decomposition():
    with patch('backend.app.services.qa.analyzer.ChatOpenAI'):
        analyzer = QAAnalyzer()
        analyzer.decomposition_chain = AsyncMock()
        # Mock JSON response
        analyzer.decomposition_chain.ainvoke.return_value = '["definition of A", "definition of B", "differences"]'
        
        result = await analyzer.decompose_query("Compare A and B", "COMPARISON")
        assert len(result) == 3
        assert result[0] == "definition of A"

if __name__ == "__main__":
    # Manually run async test if pytest not available
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_analyzer_classification())
    loop.run_until_complete(test_analyzer_decomposition())
    print("Tests passed!")
