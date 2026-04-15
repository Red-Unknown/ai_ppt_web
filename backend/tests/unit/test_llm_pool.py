import pytest
import threading
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.utils.llm_pool import (
    LLMPool,
    LLMPoolConfig,
    LLMClientWrapper,
    PoolStatus,
    PoolError,
    PoolTimeoutError,
    get_global_pool,
    initialize_pool,
    get_llm_client,
    release_llm_client,
    get_pool_status,
    shutdown_pool,
    LLMPoolContext,
)


class TestLLMPoolConfig:
    def test_default_config(self):
        config = LLMPoolConfig()
        assert config.max_connections == 20
        assert config.min_idle_connections == 5
        assert config.connection_timeout == 30.0
        assert config.idle_timeout == 300.0
        assert config.health_check_interval == 60.0

    def test_custom_config(self):
        config = LLMPoolConfig(
            max_connections=10,
            min_idle_connections=2,
            connection_timeout=10.0,
            idle_timeout=60.0,
            health_check_interval=30.0,
        )
        assert config.max_connections == 10
        assert config.min_idle_connections == 2
        assert config.connection_timeout == 10.0
        assert config.idle_timeout == 60.0
        assert config.health_check_interval == 30.0


class TestLLMClientWrapper:
    def test_wrapper_creation(self):
        mock_client = Mock()
        wrapper = LLMClientWrapper(
            client=mock_client,
            scenario="qa",
            status=PoolStatus.IDLE
        )
        assert wrapper.client is mock_client
        assert wrapper.scenario == "qa"
        assert wrapper.status == PoolStatus.IDLE
        assert wrapper.use_count == 0


class TestLLMPool:
    @pytest.fixture
    def mock_config(self):
        config = LLMPoolConfig(
            max_connections=5,
            min_idle_connections=2,
            connection_timeout=5.0,
        )
        return config

    @pytest.fixture
    def pool(self, mock_config):
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
            
            p = LLMPool(mock_config)
            yield p
            if p._initialized:
                p.shutdown()

    def test_pool_initialization(self, mock_config):
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
            
            pool = LLMPool(mock_config)
            assert pool.config.max_connections == 5
            assert pool.config.min_idle_connections == 2
            assert not pool._initialized

    def test_initialize(self, pool):
        with patch("backend.app.utils.llm_pool.ChatOpenAI") as mock_chat:
            mock_client = Mock()
            mock_chat.return_value = mock_client
            
            pool.initialize()
            
            assert pool._initialized
            assert "qa" in pool._pools
            assert "reasoner" in pool._pools

    def test_get_client_before_initialize(self, pool):
        with pytest.raises(PoolError, match="Pool not initialized"):
            pool.get_client("qa")

    def test_get_client_unknown_scenario(self, pool):
        with patch("backend.app.utils.llm_pool.ChatOpenAI"):
            pool.initialize()
            
        with pytest.raises(ValueError, match="Unknown scenario"):
            pool.get_client("unknown_scenario")

    def test_get_client_success(self, pool):
        with patch("backend.app.utils.llm_pool.ChatOpenAI") as mock_chat:
            mock_client = Mock()
            mock_chat.return_value = mock_client
            
            pool.initialize()
            client = pool.get_client("qa")
            
            assert client is mock_client
            assert len(pool._active_clients["qa"]) == 1

    def test_get_client_timeout(self, mock_config):
        import queue
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
            
            pool = LLMPool(mock_config)
            pool._initialized = True
            pool._pools["qa"] = queue.Queue(maxsize=0)
            pool._active_clients["qa"] = [None] * mock_config.max_connections
            
            with pytest.raises(PoolTimeoutError):
                pool.get_client("qa", timeout=0.1)

    def test_release_client(self, pool):
        with patch("backend.app.utils.llm_pool.ChatOpenAI") as mock_chat:
            mock_client = Mock()
            mock_chat.return_value = mock_client
            
            pool.initialize()
            client = pool.get_client("qa")
            
            pool.release_client(client)
            
            assert len(pool._active_clients["qa"]) == 0
            assert pool._pools["qa"].qsize() >= 0

    def test_release_unknown_client(self, pool):
        with patch("backend.app.utils.llm_pool.ChatOpenAI"):
            pool.initialize()
            
        mock_client = Mock()
        pool.release_client(mock_client)

    def test_get_status(self, pool):
        with patch("backend.app.utils.llm_pool.ChatOpenAI") as mock_chat:
            mock_client = Mock()
            mock_chat.return_value = mock_client
            
            pool.initialize()
            status = pool.get_status()
            
            assert "initialized" in status
            assert "scenarios" in status
            assert "qa" in status["scenarios"]

    def test_shutdown(self, pool):
        with patch("backend.app.utils.llm_pool.ChatOpenAI"):
            pool.initialize()
            
            pool.shutdown()
            
            assert pool._shutdown
            assert not pool._initialized


class TestLLMPoolContextManager:
    def test_context_manager(self):
        with patch("backend.app.utils.llm_pool.get_global_pool") as mock_get_pool:
            mock_pool = Mock()
            mock_client = Mock()
            mock_pool.get_client.return_value = mock_client
            mock_get_pool.return_value = mock_pool
            
            with LLMPoolContext("qa") as client:
                assert client is mock_client
            
            mock_pool.release_client.assert_called_once_with(mock_client)


class TestGlobalFunctions:
    def test_get_global_pool(self):
        import backend.app.utils.llm_pool as llm_pool_module
        
        original_pool = llm_pool_module._global_pool
        llm_pool_module._global_pool = None
        
        try:
            pool = get_global_pool()
            assert pool is not None
            assert isinstance(pool, LLMPool)
        finally:
            llm_pool_module._global_pool = original_pool

    def test_initialize_pool(self):
        import backend.app.utils.llm_pool as llm_pool_module
        
        original_pool = llm_pool_module._global_pool
        llm_pool_module._global_pool = None
        
        try:
            config = LLMPoolConfig(max_connections=10)
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
                
                initialize_pool(config)
                
                status = get_pool_status()
                assert status["config"]["max_connections"] == 10
                
                shutdown_pool()
        finally:
            llm_pool_module._global_pool = original_pool


class TestThreadSafety:
    def test_concurrent_get_release(self):
        import backend.app.utils.llm_pool as llm_pool_module
        
        original_pool = llm_pool_module._global_pool
        llm_pool_module._global_pool = None
        
        try:
            config = LLMPoolConfig(max_connections=10, min_idle_connections=2)
            
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
                
                initialize_pool(config)
                
                errors = []
                clients = []
                
                def get_and_release():
                    try:
                        client = get_llm_client("qa")
                        clients.append(client)
                        time.sleep(0.01)
                        release_llm_client(client)
                    except Exception as e:
                        errors.append(e)
                
                threads = []
                for _ in range(5):
                    t = threading.Thread(target=get_and_release)
                    threads.append(t)
                    t.start()
                
                for t in threads:
                    t.join()
                
                shutdown_pool()
                
                assert len(errors) == 0, f"Errors occurred: {errors}"
        finally:
            llm_pool_module._global_pool = original_pool


class TestHealthCheck:
    def test_health_check(self):
        config = LLMPoolConfig(max_connections=5, min_idle_connections=2)
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
            
            pool = LLMPool(config)
            with patch("backend.app.utils.llm_pool.ChatOpenAI") as mock_chat:
                mock_client = Mock()
                mock_chat.return_value = mock_client
                
                pool.initialize()
                result = pool.health_check()
                
                assert "qa" in result
                pool.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
