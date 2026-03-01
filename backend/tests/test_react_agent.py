import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.qa.agent import ReActAgent
from backend.app.services.qa.skills.base import BaseSkill
from langchain_core.messages import AIMessage

class MockTool(BaseSkill):
    @property
    def name(self):
        return "mock_tool"
    
    @property
    def description(self):
        return "A mock tool"
    
    async def execute(self, query: str):
        return {"status": "success", "content": f"Executed with {query}"}

@pytest.mark.asyncio
async def test_react_agent_run():
    # Setup
    # Use MagicMock for llm so bind_tools is not async by default
    mock_llm = MagicMock()
    mock_tool = MockTool()
    
    # Mock LLM responses for a 2-step loop: Thought -> Tool -> Answer
    # 1. Thought + Tool Call
    msg1 = AIMessage(content="Thinking...", tool_calls=[
        {"name": "mock_tool", "args": {"query": "test"}, "id": "call_1"}
    ])
    # 2. Final Answer
    msg2 = AIMessage(content="Final Answer")
    
    # Create a mock for the bound LLM (the result of bind_tools)
    mock_bound_llm = AsyncMock()
    mock_bound_llm.ainvoke.side_effect = [msg1, msg2]
    
    # Configure mock_llm.bind_tools to return mock_bound_llm
    mock_llm.bind_tools.return_value = mock_bound_llm
    
    agent = ReActAgent(llm=mock_llm, tools=[mock_tool])
    
    # Execute
    events = []
    async for event in agent.run("test query"):
        events.append(event)
        
    # Verify
    assert len(events) > 0
    # Check for specific event types
    event_types = [eval(e)["type"] for e in events]
    assert "thought" in event_types
    assert "tool_start" in event_types
    assert "tool_end" in event_types
    assert "answer" in event_types
    assert "done" in event_types

@pytest.mark.asyncio
async def test_react_agent_max_iterations():
    # Setup
    mock_llm = MagicMock()
    mock_tool = MockTool()
    
    # Mock LLM always returning tool calls (infinite loop)
    msg = AIMessage(content="Thinking...", tool_calls=[
        {"name": "mock_tool", "args": {"query": "test"}, "id": "call_1"}
    ])
    
    mock_bound_llm = AsyncMock()
    mock_bound_llm.ainvoke.return_value = msg
    mock_llm.bind_tools.return_value = mock_bound_llm
    
    agent = ReActAgent(llm=mock_llm, tools=[mock_tool], max_iterations=2)
    
    # Execute
    events = []
    async for event in agent.run("test query"):
        events.append(event)
        
    # Verify error on max iterations
    event_types = [eval(e)["type"] for e in events]
    assert "error" in event_types
    assert "done" in event_types
