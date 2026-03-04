import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from backend.app.services.qa.service import QAService

@pytest.fixture
def mock_qa_service():
    with patch("backend.app.services.qa.service.settings") as mock_settings:
        mock_settings.DEEPSEEK_API_KEY = "mock_key"
        mock_settings.DEEPSEEK_MODEL = "deepseek-chat"
        mock_settings.DEEPSEEK_BASE_URL = "https://api.deepseek.com"
        mock_settings.TAVILY_API_KEY = "mock_tavily"
        
        # Mock dependencies
        with patch("backend.app.services.qa.service.TreeStructureRetriever"), \
             patch("backend.app.services.qa.service.DialogueRouter"), \
             patch("backend.app.services.qa.service.QAAnalyzer"), \
             patch("backend.app.services.qa.service.SkillManager"), \
             patch("backend.app.services.qa.service.TeacherAgent"), \
             patch("backend.app.services.qa.service.prompt_loader"), \
             patch("backend.app.services.qa.service.ReActAgent"), \
             patch.object(QAService, "__init__", return_value=None):

            service = QAService()
            # Manually initialize required attributes
            service.llm_clients = {
                "summary": AsyncMock(),
                "qa": AsyncMock()
            }
            service.llm = service.llm_clients["qa"]
            return service

@pytest.mark.asyncio
async def test_predict_next_questions_success(mock_qa_service):
    with patch("backend.app.services.qa.service.ChatPromptTemplate") as MockPrompt:
        mock_chain = AsyncMock()
        # Mock valid JSON response
        mock_chain.ainvoke.return_value = '["What is the next step?", "Can you explain more?"]'
        
        mock_prompt_instance = MagicMock()
        MockPrompt.from_messages.return_value = mock_prompt_instance
        
        # Mock the pipe chain: prompt | llm | parser
        # We assume the chain construction works like: prompt | llm | parser
        # So prompt.__or__ returns intermediate, intermediate.__or__ returns chain
        mock_prompt_instance.__or__.return_value.__or__.return_value = mock_chain
        
        questions = await mock_qa_service.predict_next_questions("test query", "test answer")
        
        assert len(questions) == 2
        assert questions[0] == "What is the next step?"
        assert questions[1] == "Can you explain more?"

@pytest.mark.asyncio
async def test_predict_next_questions_markdown_json(mock_qa_service):
    with patch("backend.app.services.qa.service.ChatPromptTemplate") as MockPrompt:
        mock_chain = AsyncMock()
        # Mock Markdown JSON response
        mock_chain.ainvoke.return_value = '```json\n["Question A", "Question B"]\n```'
        
        mock_prompt_instance = MagicMock()
        MockPrompt.from_messages.return_value = mock_prompt_instance
        mock_prompt_instance.__or__.return_value.__or__.return_value = mock_chain
        
        questions = await mock_qa_service.predict_next_questions("test query", "test answer")
        
        assert questions == ["Question A", "Question B"]

@pytest.mark.asyncio
async def test_predict_next_questions_fallback_text(mock_qa_service):
    with patch("backend.app.services.qa.service.ChatPromptTemplate") as MockPrompt:
        mock_chain = AsyncMock()
        # Mock plain text list (fallback)
        mock_chain.ainvoke.return_value = "- Question 1\n* Question 2"
        
        mock_prompt_instance = MagicMock()
        MockPrompt.from_messages.return_value = mock_prompt_instance
        mock_prompt_instance.__or__.return_value.__or__.return_value = mock_chain
        
        questions = await mock_qa_service.predict_next_questions("test query", "test answer")
        
        assert questions == ["Question 1", "Question 2"]

@pytest.mark.asyncio
async def test_predict_next_questions_error_handling(mock_qa_service):
    with patch("backend.app.services.qa.service.ChatPromptTemplate") as MockPrompt:
        mock_chain = AsyncMock()
        # Mock exception
        mock_chain.ainvoke.side_effect = Exception("LLM Error")
        
        mock_prompt_instance = MagicMock()
        MockPrompt.from_messages.return_value = mock_prompt_instance
        mock_prompt_instance.__or__.return_value.__or__.return_value = mock_chain
        
        questions = await mock_qa_service.predict_next_questions("test query", "test answer")
        
        assert questions == []
