import pytest
import os
import json
from unittest.mock import MagicMock, patch
from backend.app.services.qa.service import QAService, ConfigurationError
from backend.app.core.config import settings
from backend.app.utils.cache import local_cache

# Mock Environment Variables
@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {
        "DEEPSEEK_API_KEY": "sk-mock-key",
        "DEEPSEEK_MODEL": "deepseek-chat",
        "DEEPSEEK_MAX_TOKENS": "100",
        "DEEPSEEK_TEMPERATURE": "0.5"
    }):
        yield

@pytest.fixture
def qa_service(mock_env_vars):
    # Mock settings to return values from env or just set them directly
    settings.DEEPSEEK_API_KEY = "sk-mock-key"
    settings.DEEPSEEK_MODEL = "deepseek-chat"
    
    # Mock ChatOpenAI to avoid network calls
    with patch("backend.app.services.qa.service.ChatOpenAI") as MockChat:
        service = QAService()
        yield service

def test_config_validation_error():
    # Unset API Key
    settings.DEEPSEEK_API_KEY = ""
    with pytest.raises(ConfigurationError):
        QAService()
    # Restore for other tests
    settings.DEEPSEEK_API_KEY = "sk-mock-key"

def test_llm_initialization(qa_service):
    # Check if multiple clients are initialized
    assert "qa" in qa_service.llm_clients
    assert "summary" in qa_service.llm_clients
    assert "translation" in qa_service.llm_clients
    
    # Check if specific configs are applied (we can inspect the mock calls if we want, 
    # but here we assume the logic in __init__ is correct if keys exist)
    pass

def test_prompt_versioning(qa_service):
    # Default
    qa_service.current_prompt_version = "default"
    template = qa_service.get_prompt_template()
    messages = template.messages
    assert "intelligent teaching assistant" in messages[0].prompt.template
    
    # Switch Version
    qa_service.current_prompt_version = "v2_creative"
    template_v2 = qa_service.get_prompt_template()
    messages_v2 = template_v2.messages
    assert "creative and engaging tutor" in messages_v2[0].prompt.template

def test_local_cache():
    local_cache.clear()
    
    # Test Set/Get
    prompt = "What is physics?"
    params = {"user_id": "u1"}
    response = "Physics is the study of matter."
    
    local_cache.set(prompt, params, response)
    
    cached = local_cache.get(prompt, params)
    assert cached == response
    
    # Test Cache Miss with different params
    cached_miss = local_cache.get(prompt, {"user_id": "u2"})
    assert cached_miss is None
    
    # Test Metrics
    metrics = local_cache.get_metrics()
    assert metrics["hits"] == 1
    assert metrics["misses"] == 1

@pytest.mark.asyncio
async def test_stream_answer_cache_hit(qa_service):
    # Setup Cache
    request_mock = MagicMock()
    request_mock.query = "Cached Question"
    request_mock.top_k = 3
    request_mock.session_id = "sess_1"
    request_mock.current_path = "root"
    
    local_cache.set("Cached Question", {"user_id": "student_001", "top_k": 3}, "Cached Answer")
    
    # Consume Generator
    chunks = []
    async for chunk in qa_service.stream_answer_question(request_mock):
        data = json.loads(chunk)
        chunks.append(data)
    
    # Verify Cache Hit Action
    actions = [c.get("action") for c in chunks if c.get("type") == "start"]
    assert "DISK_CACHE_HIT" in actions
    
    # Verify Content
    content = "".join([c.get("content", "") for c in chunks if c.get("type") == "token"])
    assert "Cached Answer" == content

if __name__ == "__main__":
    # Manually run tests if needed via python
    pass
