import pytest
import asyncio
import json
from unittest import mock
from backend.app.schemas.qa import ChatRequest, Intent
from backend.app.services.qa.service import QAService

@pytest.mark.asyncio
async def test_reasoner_mode_switching():
    """Test that complex queries trigger reasoner mode."""
    
    # Mock settings and LLM to avoid actual calls
    with mock.patch("backend.app.core.config.settings.DEEPSEEK_API_KEY", "test-key"):
        service = QAService()
        
        # Mock dependencies
        service.router = mock.Mock()
        service.router.route.return_value = Intent.QA # Force QA route (Enum)
        
        service.analyzer = mock.AsyncMock()
        service.analyzer.analyze.return_value = "MATH" # Force MATH intent (complex)
        
        service.skill_manager = mock.Mock()
        service.skill_manager.get_skill.return_value = None # No skill, direct LLM
        
        # Mock LLM stream response
        mock_llm = mock.AsyncMock()
        
        # Create a mock chunk with reasoning content
        class MockChunk:
            def __init__(self, content, reasoning=""):
                self.content = content
                self.additional_kwargs = {"reasoning_content": reasoning} if reasoning else {}
                self.response_metadata = {}

        # Simulate stream: Status -> Reasoning -> Content
        async def mock_astream(*args, **kwargs):
            yield MockChunk("", reasoning="Thinking step 1...")
            yield MockChunk("", reasoning="Thinking step 2...")
            yield MockChunk("The answer is 42.")
            
        mock_llm.astream = mock_astream
        
        # Inject mock LLM into the 'reasoner' slot
        service.llm_clients["reasoner"] = mock_llm
        
        # Create request (default model="deepseek")
        request = ChatRequest(query="Calculate the trajectory...")
        
        # Run stream
        messages = []
        async for msg in service.stream_answer_question(request):
            messages.append(json.loads(msg))
            
        # Verify mode switch message
        status_msgs = [m for m in messages if m["type"] == "status"]
        assert any("深度思考模式" in m["content"] for m in status_msgs), "Should switch to reasoner mode"
        
        # Verify reasoning content
        reasoning_msgs = [m for m in messages if m["type"] == "reasoning"]
        assert len(reasoning_msgs) >= 2
        assert reasoning_msgs[0]["content"] == "Thinking step 1..."
        
        # Verify final answer
        token_msgs = [m for m in messages if m["type"] == "token"]
        assert "".join(m["content"] for m in token_msgs) == "The answer is 42."

@pytest.mark.asyncio
async def test_standard_mode_no_switching():
    """Test that simple queries stay in standard mode."""
    
    with mock.patch("backend.app.core.config.settings.DEEPSEEK_API_KEY", "test-key"):
        service = QAService()
        
        # Mock dependencies
        service.router = mock.Mock()
        service.router.route.return_value = Intent.QA
        
        service.analyzer = mock.AsyncMock()
        service.analyzer.analyze.return_value = "FACTUAL" # Simple intent
        
        service.skill_manager = mock.Mock()
        service.skill_manager.get_skill.return_value = None
        
        # Mock LLM for standard mode
        mock_llm = mock.AsyncMock()
        service.llm_clients["qa"] = mock_llm
        service.llm = mock_llm # Standard mode uses self.llm
        
        # Since standard mode constructs a chain with StrOutputParser,
        # we need to mock the chain execution or prevent it.
        # But we only care about the mode switching logic which happens BEFORE chain.
        # The logic emits a status message if switching.
        
        # We'll mock the chain to just stop iteration immediately or raise exception we catch
        # Actually, if we mock `llm.astream` to yield simple strings, `StrOutputParser` might complain 
        # because it expects `AIMessageChunk`.
        # So let's mock `llm.astream` to yield AIMessageChunk.
        
        class MockMessageChunk:
            content = "Simple answer."
            def __add__(self, other): return self
            
        mock_llm.astream.return_value = iter([MockMessageChunk()])
        
        request = ChatRequest(query="What is the capital of France?")
        
        messages = []
        try:
            async for msg in service.stream_answer_question(request):
                messages.append(json.loads(msg))
        except Exception:
            pass
            
        status_msgs = [m for m in messages if m["type"] == "status"]
        # Should NOT have "切换至深度思考模式"
        assert not any("深度思考模式" in m["content"] for m in status_msgs)
