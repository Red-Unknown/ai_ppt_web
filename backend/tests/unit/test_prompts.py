import os
import json
import pytest
from unittest.mock import patch, MagicMock
from backend.app.core import prompt_loader
from backend.app.core.config import settings
from backend.app.services.qa.service import QAService
from backend.app.schemas.qa import ChatRequest
from langchain_core.documents import Document


def test_prompt_loader_versions():
    versions = prompt_loader.list_versions()
    assert "v5_enhanced_zh" in versions
    assert "v2_creative_zh" in versions
    sys_text = prompt_loader.get_prompt("default", "system")
    user_text = prompt_loader.get_prompt("default", "user")
    assert "{context}" in sys_text
    assert "{question}" in user_text


@pytest.mark.asyncio
async def test_console_like_flow_with_mock():
    # Mock AppContext and session_id_ctx
    with patch("backend.app.services.qa.service.session_id_ctx") as mock_ctx:
        mock_ctx.set = MagicMock()
        mock_ctx.reset = MagicMock()
        
        os.environ.setdefault("DEEPSEEK_API_KEY", "sk-mock-key")
    os.environ.setdefault("DEEPSEEK_MODEL", "deepseek-chat")
    with patch("backend.app.services.qa.service.ChatOpenAI"):
        svc = QAService()
        req = ChatRequest(query="课程介绍", session_id="s1", current_path="力学/牛顿定律", top_k=2)
        chunks = []
        async for chunk in svc.stream_answer_question(req, user_id="u1"):
            chunks.append(json.loads(chunk))
        suggestions = [c for c in chunks if c.get("type") == "suggestions"]
        assert len(suggestions) == 1
