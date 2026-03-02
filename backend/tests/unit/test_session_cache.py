import pytest
from backend.app.services.session.manager import SessionManager

def test_session_cache():
    user_id = "test_user"
    session_id = SessionManager.create_chat_session(user_id)
    
    query = "test query"
    docs = [{"content": "doc1"}]
    
    # Test Cache Miss
    assert SessionManager.get_cached_docs(session_id, query) is None
    
    # Test Cache Write
    SessionManager.cache_docs(session_id, query, docs)
    
    # Test Cache Hit
    cached = SessionManager.get_cached_docs(session_id, query)
    assert cached == docs
    
    # Test Fingerprint (Case Insensitive)
    cached_upper = SessionManager.get_cached_docs(session_id, query.upper())
    assert cached_upper == docs

def test_search_limit():
    user_id = "test_user"
    session_id = SessionManager.create_chat_session(user_id)
    
    assert SessionManager.is_search_used(session_id) is False
    
    SessionManager.mark_search_used(session_id)
    
    assert SessionManager.is_search_used(session_id) is True
