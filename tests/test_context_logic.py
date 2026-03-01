import pytest
import json
from unittest.mock import MagicMock, patch
from backend.app.services.qa.service import QAService
from backend.app.services.student.state_manager import StudentStateManager, redis_client

@pytest.fixture
def qa_service():
    # Mock settings to avoid configuration errors
    with patch("backend.app.core.config.settings") as mock_settings:
        mock_settings.DEEPSEEK_API_KEY = "mock_key"
        mock_settings.TAVILY_API_KEY = "mock_tavily"
        mock_settings.DEEPSEEK_MODEL = "deepseek-chat"
        
        service = QAService()
        return service

def test_truncate_history_by_tokens(qa_service):
    """Test that history is truncated correctly based on token limit."""
    
    # Create a long history
    history = []
    for i in range(50):
        history.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"Message {i} " * 10  # Approx 20-30 tokens per message
        })
        
    # Test with a large limit (should keep all)
    truncated_all = qa_service._truncate_history_by_tokens(history, max_tokens=10000)
    assert len(truncated_all.split("\n")) == 50
    assert "Message 0" in truncated_all
    assert "Message 49" in truncated_all
    
    # Test with a small limit (should keep only recent)
    # Each message is "Message X " * 10. "Message" is 1 token, " X" is 1 token.
    # So "Message X " * 10 is roughly 20-30 tokens.
    # Let's say we want to keep approx 5 messages. 5 * 30 = 150 tokens.
    truncated_small = qa_service._truncate_history_by_tokens(history, max_tokens=150)
    
    lines = truncated_small.split("\n")
    assert len(lines) < 50
    assert len(lines) > 0
    # Should contain the most recent message
    assert "Message 49" in truncated_small
    # Should NOT contain the oldest message
    assert "Message 0" not in truncated_small

def test_50_turns_simulation(qa_service):
    """Simulate 50 turns of conversation and verify context construction."""
    session_id = "test_session_50_turns"
    
    # Clear previous state
    redis_client.delete(StudentStateManager._get_history_key(session_id))
    
    # Simulate 50 turns (User + Assistant = 100 messages total if we consider turns as pairs, 
    # but "50 轮连续对话" usually means 50 exchanges. 
    # Let's add 50 user messages and 50 assistant messages.)
    
    for i in range(50):
        StudentStateManager.add_history(session_id, "user", f"Question {i}")
        StudentStateManager.add_history(session_id, "assistant", f"Answer {i}")
        
    # Verify history in StateManager (limit is 100, so we expect 100 messages total in storage)
    stored_history = StudentStateManager.get_history(session_id, limit=200)
    assert len(stored_history) == 100 # Because add_history caps at 100
    
    # The stored history should be the ALL 100 messages (Question 0..49, Answer 0..49)
    assert stored_history[0]["content"] == "Question 0"
    assert stored_history[-1]["content"] == "Answer 49"
    
    # Now verify QAService truncation
    # Even with 100 messages, if they are long, they might be truncated further by token limit.
    # Our messages are short ("Question X"), so they should all fit in 2000 tokens.
    
    history_str = qa_service._truncate_history_by_tokens(stored_history, max_tokens=2000)
    assert "Question 0" in history_str
    assert "Answer 49" in history_str
    
    # Now test with long messages to force token truncation
    redis_client.delete(StudentStateManager._get_history_key(session_id))
    long_content = "Word " * 100 # ~100 tokens
    for i in range(50):
        StudentStateManager.add_history(session_id, "user", f"User {i} {long_content}")
        # Only add user messages to hit the 50 limit with just user messages for simplicity
        
    stored_history = StudentStateManager.get_history(session_id, limit=100)
    assert len(stored_history) == 50
    
    # 50 messages * 100 tokens = 5000 tokens.
    # Limit is 2000. Should truncate.
    history_str = qa_service._truncate_history_by_tokens(stored_history, max_tokens=2000)
    
    # Should have roughly 20 messages (2000 / 100 = 20)
    assert history_str.count("User") < 50
    assert history_str.count("User") > 10 # Should have at least some
    
    # Verify the LAST message is present
    assert "User 49" in history_str
    # Verify the FIRST stored message (User 0 or User 25 depending on previous logic) is NOT present
    # stored_history[0] is User 0 (since we cleared and added 50).
    # But wait, add_history caps at 50. So User 0 is in stored_history.
    # But token truncation should remove it.
    assert "User 0" not in history_str

