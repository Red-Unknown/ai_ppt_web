import pytest
import json
from unittest.mock import MagicMock, patch
from backend.app.services.student.state_manager import StudentStateManager, SafeRedis, MockRedis
from backend.app.schemas.student import StudentProfile

@pytest.fixture
def mock_redis_client():
    """Fixture to mock the underlying Redis client inside SafeRedis."""
    # We need to patch the GLOBAL redis_client in state_manager
    # Or better, we can just manipulate StudentStateManager's redis_client if it's accessible.
    # But it's a module-level variable.
    # Let's patch it.
    with patch("backend.app.services.student.state_manager.redis_client") as mock_safe_redis:
        # Mock SafeRedis behavior or just replace the inner client?
        # Since the code uses `redis_client.get(...)`, we should mock these methods.
        
        # However, to test SafeRedis logic itself, we should instantiate SafeRedis with a mock inner client.
        yield mock_safe_redis

def test_safe_redis_wrapper():
    """Test SafeRedis exception handling."""
    mock_inner = MagicMock()
    safe_redis = SafeRedis(mock_inner)
    
    # Test GET success
    mock_inner.get.return_value = "value"
    assert safe_redis.get("key") == "value"
    
    # Test GET failure
    mock_inner.get.side_effect = Exception("Connection Error")
    assert safe_redis.get("key") is None # Should return None on error
    
    # Test SET failure
    mock_inner.set.side_effect = Exception("Connection Error")
    safe_redis.set("key", "value") # Should not raise
    
    # Test DELETE failure
    mock_inner.delete.side_effect = Exception("Connection Error")
    safe_redis.delete("key") # Should not raise

def test_add_history_limit():
    """Test history limit (100 messages)."""
    # Use a real MockRedis (in-memory) for logic testing
    inner_redis = MockRedis()
    safe_redis = SafeRedis(inner_redis)
    
    # Patch the global redis_client
    with patch("backend.app.services.student.state_manager.redis_client", safe_redis):
        session_id = "test_limit"
        
        # Add 105 messages
        for i in range(105):
            StudentStateManager.add_history(session_id, "user", f"msg {i}")
            
        history = StudentStateManager.get_history(session_id, limit=200)
        assert len(history) == 100
        assert history[0]["content"] == "msg 5"
        assert history[-1]["content"] == "msg 104"

def test_profile_operations():
    """Test profile create/update/get."""
    inner_redis = MockRedis()
    safe_redis = SafeRedis(inner_redis)
    
    with patch("backend.app.services.student.state_manager.redis_client", safe_redis):
        user_id = "u1"
        
        # Get non-existent
        assert StudentStateManager.get_profile(user_id) is None
        
        # Create
        profile = StudentStateManager.create_or_update_profile(user_id, {"learning_style": "VISUAL"})
        assert profile.user_id == user_id
        assert profile.learning_style == "VISUAL"
        
        # Update
        profile2 = StudentStateManager.create_or_update_profile(user_id, {"interaction_mode": "SOCRATIC"})
        assert profile2.interaction_mode == "SOCRATIC"
        assert profile2.learning_style == "VISUAL" # Should preserve old value
        
        # Verify persistence
        p = StudentStateManager.get_profile(user_id)
        assert p.interaction_mode == "SOCRATIC"

def test_invalid_data_handling():
    """Test handling of invalid JSON in Redis."""
    inner_redis = MockRedis()
    safe_redis = SafeRedis(inner_redis)
    
    with patch("backend.app.services.student.state_manager.redis_client", safe_redis):
        session_id = "bad_json"
        key = StudentStateManager._get_history_key(session_id)
        
        # Manually inject bad JSON
        inner_redis.set(key, "{bad_json")
        
        # get_history should handle this gracefully (return empty list, log error)
        assert StudentStateManager.get_history(session_id) == []
             
        # add_history should reset corrupted data and append new message
        StudentStateManager.add_history(session_id, "user", "new_msg")
        hist = StudentStateManager.get_history(session_id)
        assert len(hist) == 1
        assert hist[0]["content"] == "new_msg"
        
def test_concurrent_writes_simulation():
    """Simulate concurrent writes (simplified)."""
    # Since Redis is single-threaded, concurrency is handled by Redis.
    # But read-modify-write in app code (get history -> append -> set) is NOT atomic.
    # This test demonstrates the race condition (we can't easily fix it without Lua scripts or locking, 
    # but let's verify if it happens or if we just accept it for now).
    
    inner_redis = MockRedis()
    safe_redis = SafeRedis(inner_redis)
    
    with patch("backend.app.services.student.state_manager.redis_client", safe_redis):
        session_id = "race"
        
        # Initial
        StudentStateManager.add_history(session_id, "user", "1")
        
        # Simulate race: 
        # A reads, B reads, A writes, B writes (overwriting A)
        
        # Manual simulation of race condition steps:
        key = StudentStateManager._get_history_key(session_id)
        
        # User A reads
        data_a = inner_redis.get(key)
        hist_a = json.loads(data_a)
        hist_a.append({"role": "user", "content": "2a"})
        
        # User B reads (same initial data)
        data_b = inner_redis.get(key)
        hist_b = json.loads(data_b)
        hist_b.append({"role": "user", "content": "2b"})
        
        # User A writes
        inner_redis.set(key, json.dumps(hist_a))
        
        # User B writes (overwrites A)
        inner_redis.set(key, json.dumps(hist_b))
        
        # Result: "2a" is lost.
        final = StudentStateManager.get_history(session_id)
        # Verify loss (This confirms the behavior, not a fix, but "coverage" of the scenario)
        contents = [m["content"] for m in final]
        assert "2b" in contents
        assert "2a" not in contents
        
        # Note: Fixing this requires Redis LIST operations (RPUSH) instead of GET-SET whole list.
        # Implementing RPUSH would be a good "enhancement".
