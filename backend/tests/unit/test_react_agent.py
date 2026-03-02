import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.qa.agents.react import ReActAgent
from backend.app.services.qa.tools.base import BaseSkill
from langchain_core.messages import AIMessage, AIMessageChunk

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
    # 1. Thought + Tool Call (Streamed)
    # ReActAgent expects AIMessageChunk with tool_call_chunks
    
    # Chunk 1: Thinking
    chunk1 = AIMessageChunk(content="Thinking...")
    chunk1.tool_call_chunks = []
    
    # Chunk 2: Tool Call Start
    chunk2 = AIMessageChunk(content="")
    chunk2.tool_call_chunks = [
        {"name": "mock_tool", "args": "{\"query\": \"test\"}", "id": "call_1", "index": 0}
    ]
    
    # 2. Final Answer
    chunk3 = AIMessageChunk(content="Final Answer")
    chunk3.tool_call_chunks = []
    
    # Create a mock for the bound LLM (the result of bind_tools)
    mock_bound_llm = AsyncMock()
    # mock_bound_llm.ainvoke.side_effect = [msg1, msg2]
    
    # Mock astream to yield chunks
    async def mock_astream(*args, **kwargs):
        nonlocal call_count
        if call_count == 0:
            yield chunk1
            yield chunk2
        else:
            yield chunk3
        call_count += 1
        
    call_count = 0
    mock_bound_llm.astream = mock_astream
    
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
    assert "thought_stream" in event_types
    assert "tool_start" in event_types
    assert "tool_result" in event_types
    # assert "answer" in event_types # ReActAgent streams answer via thought_stream
    assert "done" in event_types

@pytest.mark.asyncio
async def test_react_agent_max_iterations():
    # Setup
    mock_llm = MagicMock()
    mock_tool = MockTool()
    
    # Mock LLM always returning tool calls (infinite loop)
    chunk = AIMessageChunk(content="Thinking...")
    chunk.tool_call_chunks = [
        {"name": "mock_tool", "args": "{\"query\": \"test\"}", "id": "call_1", "index": 0}
    ]
    
    mock_bound_llm = AsyncMock()
    
    # Mock astream to always yield the tool call chunk
    async def mock_astream_infinite(*args, **kwargs):
        yield chunk
        
    mock_bound_llm.astream = mock_astream_infinite
    
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
