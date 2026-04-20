import pytest
import asyncio
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import List, Union, Dict
from dataclasses import asdict

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.utils.llm_pool import (
    LLMInvoker,
    StreamChunk,
    create_invoker,
    chat,
    achat,
    stream_chat,
    astream_chat,
    LLMInvokeError,
    get_global_pool,
    shutdown_pool,
    initialize_pool,
    LLMPoolConfig,
)
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class TestStreamChunk:
    def test_stream_chunk_creation(self):
        chunk = StreamChunk(content="Hello", reasoning="Thinking")
        assert chunk.content == "Hello"
        assert chunk.reasoning == "Thinking"
        assert chunk.to_string() == "Hello"

    def test_stream_chunk_to_string(self):
        chunk = StreamChunk(content="Test content")
        assert chunk.to_string() == "Test content"

    def test_stream_chunk_with_usage(self):
        chunk = StreamChunk(
            content="Answer",
            reasoning=None,
            usage={"prompt_tokens": 10, "completion_tokens": 5},
            finish_reason="stop"
        )
        assert chunk.usage == {"prompt_tokens": 10, "completion_tokens": 5}
        assert chunk.finish_reason == "stop"


class TestLLMInvokerCreation:
    def test_create_invoker_default(self):
        invoker = create_invoker()
        assert invoker.scenario == "qa"
        assert invoker.model is None

    def test_create_invoker_with_model(self):
        invoker = create_invoker(scenario="reasoner", model="deepseek-reasoner")
        assert invoker.scenario == "reasoner"
        assert invoker.model == "deepseek-reasoner"

    def test_create_invoker_with_qwen(self):
        invoker = create_invoker(model="qwen")
        assert invoker.model == "qwen"


class TestLLMInvokerChat:
    @pytest.fixture
    def mock_pool(self):
        with patch("backend.app.utils.llm_pool.get_global_pool") as mock_get_pool:
            mock_pool = Mock()
            mock_config = {
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 4000,
                "api_key": "test-key",
                "base_url": "https://api.deepseek.com"
            }
            mock_pool.get_scenario_config.return_value = mock_config
            mock_get_pool.return_value = mock_pool
            yield mock_pool

    def test_chat_with_string_messages(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = "Hello, how can I help you?"
            mock_client.invoke.return_value = mock_response
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            result = invoker.chat(["Hello"])

            assert result == "Hello, how can I help you?"
            mock_client.invoke.assert_called_once()

    def test_chat_with_dict_messages(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = "Response text"
            mock_client.invoke.return_value = mock_response
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            result = invoker.chat([{"role": "user", "content": "Hello"}])

            assert result == "Response text"

    def test_chat_with_langchain_messages(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = "Response text"
            mock_client.invoke.return_value = mock_response
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            result = invoker.chat([HumanMessage(content="Hello")])

            assert result == "Response text"

    def test_chat_with_custom_temperature(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = "Response"
            mock_client.invoke.return_value = mock_response
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            result = invoker.chat(["Hello"], temperature=0.5)

            call_kwargs = mock_client.invoke.call_args[1]
            assert call_kwargs.get("temperature") == 0.5

    def test_chat_error_handling(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_client.invoke.side_effect = Exception("API Error")
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            with pytest.raises(LLMInvokeError, match="LLM调用失败"):
                invoker.chat(["Hello"])


class TestLLMInvokerAsyncChat:
    @pytest.fixture
    def mock_pool(self):
        with patch("backend.app.utils.llm_pool.get_global_pool") as mock_get_pool:
            mock_pool = Mock()
            mock_config = {
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 4000,
                "api_key": "test-key",
                "base_url": "https://api.deepseek.com"
            }
            mock_pool.get_scenario_config.return_value = mock_config
            mock_get_pool.return_value = mock_pool
            yield mock_pool

    @pytest.mark.asyncio
    async def test_achat_with_string_messages(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.content = "Async response"
            mock_client.ainvoke = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            result = await invoker.achat(["Hello"])

            assert result == "Async response"

    @pytest.mark.asyncio
    async def test_achat_error_handling(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_client.ainvoke = AsyncMock(side_effect=Exception("API Error"))
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            with pytest.raises(LLMInvokeError, match="LLM异步调用失败"):
                await invoker.achat(["Hello"])


class TestLLMInvokerStreamChat:
    @pytest.fixture
    def mock_pool(self):
        with patch("backend.app.utils.llm_pool.get_global_pool") as mock_get_pool:
            mock_pool = Mock()
            mock_config = {
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 4000,
                "api_key": "test-key",
                "base_url": "https://api.deepseek.com"
            }
            mock_pool.get_scenario_config.return_value = mock_config
            mock_get_pool.return_value = mock_pool
            yield mock_pool

    def test_stream_chat_returns_generator(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()

            def mock_stream(*args, **kwargs):
                chunks = [
                    Mock(content="Hello "),
                    Mock(content="world!"),
                ]
                for chunk in chunks:
                    yield chunk

            mock_client.stream = mock_stream
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            results = list(invoker.stream_chat(["Hello"]))

            assert len(results) == 2
            assert results[0].content == "Hello "
            assert results[1].content == "world!"

    def test_stream_chat_with_reasoning(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()

            def mock_stream(*args, **kwargs):
                chunk = Mock(content="Answer")
                chunk.additional_kwargs = {"reasoning_content": "Thinking..."}
                yield chunk

            mock_client.stream = mock_stream
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            results = list(invoker.stream_chat(["Question"]))

            assert len(results) == 1
            assert results[0].content == "Answer"
            assert results[0].reasoning == "Thinking..."

    def test_stream_chat_error_handling(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()

            def mock_stream(*args, **kwargs):
                raise Exception("Stream Error")

            mock_client.stream = mock_stream
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            with pytest.raises(LLMInvokeError, match="LLM流式调用失败"):
                list(invoker.stream_chat(["Hello"]))


class TestLLMInvokerAsyncStreamChat:
    @pytest.fixture
    def mock_pool(self):
        with patch("backend.app.utils.llm_pool.get_global_pool") as mock_get_pool:
            mock_pool = Mock()
            mock_config = {
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 4000,
                "api_key": "test-key",
                "base_url": "https://api.deepseek.com"
            }
            mock_pool.get_scenario_config.return_value = mock_config
            mock_get_pool.return_value = mock_pool
            yield mock_pool

    @pytest.mark.asyncio
    async def test_astream_chat(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = AsyncMock()

            async def mock_astream(*args, **kwargs):
                chunks = [
                    Mock(content="Async "),
                    Mock(content="stream!"),
                ]
                for chunk in chunks:
                    yield chunk

            mock_client.astream = mock_astream
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")
            results = []
            async for chunk in invoker.astream_chat(["Hello"]):
                results.append(chunk)

            assert len(results) == 2
            assert results[0].content == "Async "
            assert results[1].content == "stream!"

    @pytest.mark.asyncio
    async def test_astream_chat_error_handling(self, mock_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            mock_client = Mock()

            async def mock_astream(*args, **kwargs):
                raise Exception("Async Stream Error")

            mock_client.astream = mock_astream
            mock_get_client.return_value = mock_client

            invoker = LLMInvoker(scenario="qa")

            with pytest.raises(LLMInvokeError, match="LLM异步流式调用失败"):
                async for _ in invoker.astream_chat(["Hello"]):
                    pass


class TestLLMInvokerStreamReasoning:
    @pytest.fixture
    def mock_reasoner_pool(self):
        with patch("backend.app.utils.llm_pool.get_global_pool") as mock_get_pool:
            mock_pool = Mock()
            mock_config = {
                "model": "deepseek-reasoner",
                "temperature": 0.6,
                "max_tokens": 4000,
                "api_key": "test-key",
                "base_url": "https://api.deepseek.com"
            }
            mock_pool.get_scenario_config.return_value = mock_config
            mock_get_pool.return_value = mock_pool
            yield mock_pool

    @pytest.mark.asyncio
    async def test_astream_reasoner_with_reasoning(self, mock_reasoner_pool):
        with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
            with patch("backend.app.utils.llm_pool.AsyncOpenAI") as MockAsyncOpenAI:
                mock_client = Mock()
                mock_client_instance = Mock()

                mock_chunk = Mock()
                mock_chunk.choices = [Mock()]
                mock_chunk.choices[0].delta = Mock()
                mock_chunk.choices[0].delta.reasoning_content = "Reasoning process..."
                mock_chunk.choices[0].delta.content = "Final answer"
                mock_chunk.choices[0].finish_reason = "stop"

                async def mock_async_generator():
                    yield mock_chunk

                mock_stream = Mock()
                mock_stream.__aiter__ = lambda self: mock_async_generator()

                mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_stream)
                mock_client.chat.completions = mock_client_instance
                MockAsyncOpenAI.return_value = mock_client_instance

                mock_get_client.return_value = mock_client

                invoker = LLMInvoker(scenario="reasoner", model="deepseek-reasoner")
                results = []
                async for chunk in invoker.astream_reasoning(["Question"]):
                    results.append(chunk)

                assert len(results) > 0


class TestShortcutFunctions:
    @pytest.fixture
    def mock_invoker(self):
        with patch("backend.app.utils.llm_pool.LLMInvoker") as MockInvoker:
            mock_instance = Mock()
            mock_instance.chat.return_value = "Chat result"
            MockInvoker.return_value = mock_instance
            yield mock_instance

    def test_chat_function(self, mock_invoker):
        result = chat([{"role": "user", "content": "Hello"}], model="deepseek")
        assert result == "Chat result"
        mock_invoker.chat.assert_called_once()

    def test_chat_function_closes_client(self, mock_invoker):
        chat([{"role": "user", "content": "Hello"}], model="deepseek")
        mock_invoker.close.assert_called_once()


class TestMessageConversion:
    @pytest.fixture
    def mock_pool(self):
        with patch("backend.app.utils.llm_pool.get_global_pool") as mock_get_pool:
            mock_pool = Mock()
            mock_config = {
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 4000,
                "api_key": "test-key",
                "base_url": "https://api.deepseek.com"
            }
            mock_pool.get_scenario_config.return_value = mock_config
            mock_get_pool.return_value = mock_pool
            yield mock_pool

    def test_convert_string_message(self, mock_pool):
        invoker = LLMInvoker(scenario="qa")
        result = invoker._convert_to_langchain_messages(["Hello"])
        assert len(result) == 1
        assert isinstance(result[0], HumanMessage)
        assert result[0].content == "Hello"

    def test_convert_dict_message(self, mock_pool):
        invoker = LLMInvoker(scenario="qa")
        result = invoker._convert_to_langchain_messages([{"role": "user", "content": "Hello"}])
        assert len(result) == 1
        assert isinstance(result[0], HumanMessage)

    def test_convert_system_message(self, mock_pool):
        invoker = LLMInvoker(scenario="qa")
        result = invoker._convert_to_langchain_messages([{"role": "system", "content": "You are helpful"}])
        assert len(result) == 1
        assert isinstance(result[0], SystemMessage)

    def test_convert_assistant_message(self, mock_pool):
        invoker = LLMInvoker(scenario="qa")
        result = invoker._convert_to_langchain_messages([{"role": "assistant", "content": "I can help"}])
        assert len(result) == 1
        assert isinstance(result[0], AIMessage)

    def test_convert_mixed_messages(self, mock_pool):
        invoker = LLMInvoker(scenario="qa")
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            "Direct string",
            HumanMessage(content="LangChain message"),
        ]
        result = invoker._convert_to_langchain_messages(messages)
        assert len(result) == 4


class TestContentExtraction:
    @pytest.fixture
    def invoker(self):
        return LLMInvoker(scenario="qa")

    def test_extract_from_response_with_content(self, invoker):
        response = Mock()
        response.content = "Response text"
        result = invoker._extract_content(response)
        assert result == "Response text"

    def test_extract_from_stream_chunk(self, invoker):
        chunk = StreamChunk(content="Chunk text")
        result = invoker._extract_content(chunk)
        assert result == "Chunk text"

    def test_extract_from_string(self, invoker):
        result = invoker._extract_content("String response")
        assert result == "String response"

    def test_extract_reasoning_from_additional_kwargs(self, invoker):
        chunk = Mock()
        chunk.additional_kwargs = {"reasoning_content": "Thinking..."}
        result = invoker._extract_reasoning(chunk)
        assert result == "Thinking..."

    def test_extract_reasoning_from_response_metadata(self, invoker):
        chunk = Mock()
        chunk.additional_kwargs = {}
        chunk.response_metadata = {"reasoning_content": "Reasoning..."}
        result = invoker._extract_reasoning(chunk)
        assert result == "Reasoning..."

    def test_extract_reasoning_from_reasoning_content_field(self, invoker):
        chunk = Mock()
        chunk.additional_kwargs = {}
        chunk.response_metadata = {}
        chunk.reasoning_content = "Direct reasoning"
        result = invoker._extract_reasoning(chunk)
        assert result == "Direct reasoning"


class TestLLMInvokerClose:
    def test_close_releases_client(self):
        with patch("backend.app.utils.llm_pool.get_global_pool") as mock_get_pool:
            with patch("backend.app.utils.llm_pool.get_llm_client") as mock_get_client:
                with patch("backend.app.utils.llm_pool.release_llm_client") as mock_release:
                    mock_client = Mock()
                    mock_get_client.return_value = mock_client

                    invoker = LLMInvoker(scenario="qa")
                    invoker._client = mock_client
                    invoker.close()

                    mock_release.assert_called_once_with(mock_client)
                    assert invoker._client is None

    def test_close_twice_is_safe(self):
        invoker = LLMInvoker(scenario="qa")
        invoker._client = None
        invoker.close()
        invoker.close()


class TestIntegration:
    def test_full_chat_flow_with_mock(self):
        import backend.app.utils.llm_pool as llm_pool_module

        original_pool = llm_pool_module._global_pool
        llm_pool_module._global_pool = None

        try:
            config = LLMPoolConfig(max_connections=5, min_idle_connections=1)
            with patch("backend.app.utils.llm_pool.settings") as mock_settings:
                mock_settings.DEEPSEEK_API_KEY = "test-key"
                mock_settings.DEEPSEEK_MODEL = "deepseek-chat"
                mock_settings.DEEPSEEK_REASONER_MODEL = "deepseek-reasoner"
                mock_settings.DEEPSEEK_MAX_TOKENS = 4000
                mock_settings.DEEPSEEK_TEMPERATURE = 0.7
                mock_settings.DEEPSEEK_BASE_URL = "https://api.deepseek.com"
                mock_settings.KIMI_API_KEY = ""
                mock_settings.OPENAI_API_KEY = ""
                mock_settings.KIMI_MODEL = "moonshot-v1-8k"
                mock_settings.KIMI_BASE_URL = "https://api.moonshot.cn/v1"
                mock_settings.KIMI_MAX_TOKENS = 8000
                mock_settings.KIMI_TEMPERATURE = 0.7

                with patch("backend.app.utils.llm_pool.ChatOpenAI") as mock_chat:
                    mock_client = Mock()
                    mock_response = Mock()
                    mock_response.content = "Integration test response"
                    mock_client.invoke.return_value = mock_response
                    mock_client.stream.return_value = iter([
                        Mock(content="Part "),
                        Mock(content="1"),
                    ])
                    mock_chat.return_value = mock_client

                    initialize_pool(config)

                    invoker = LLMInvoker(scenario="qa")
                    result = invoker.chat([{"role": "user", "content": "Test"}])
                    assert result == "Integration test response"

                    stream_results = list(invoker.stream_chat([{"role": "user", "content": "Test"}]))
                    assert len(stream_results) == 2
                    assert stream_results[0].content == "Part "
                    assert stream_results[1].content == "1"

                    invoker.close()
                    shutdown_pool()
        finally:
            llm_pool_module._global_pool = original_pool


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
