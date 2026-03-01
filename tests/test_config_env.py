import os
import pytest
from unittest import mock
from backend.app.core.config import Settings
from backend.app.services.qa.service import QAService, ConfigurationError

# Helper to clear environment
@pytest.fixture
def clean_env():
    old_env = os.environ.copy()
    if "DEEPSEEK_API_KEY" in os.environ:
        del os.environ["DEEPSEEK_API_KEY"]
    if "TAVILY_API_KEY" in os.environ:
        del os.environ["TAVILY_API_KEY"]
    yield
    os.environ.clear()
    os.environ.update(old_env)

def test_settings_load_from_env(clean_env):
    """Test that Settings loads values from environment variables."""
    os.environ["DEEPSEEK_API_KEY"] = "test-key-123"
    os.environ["TAVILY_API_KEY"] = "tavily-key-456"
    
    # Reload settings
    settings = Settings()
    
    assert settings.DEEPSEEK_API_KEY == "test-key-123"
    assert settings.TAVILY_API_KEY == "tavily-key-456"

def test_service_validation_failure(clean_env):
    """Test that QAService raises ConfigurationError when DEEPSEEK_API_KEY is missing."""
    # Ensure no key is set
    with mock.patch("backend.app.core.config.settings.DEEPSEEK_API_KEY", ""):
        with pytest.raises(ConfigurationError) as excinfo:
            QAService()
        assert "Missing required configuration" in str(excinfo.value)
        assert "DEEPSEEK_API_KEY" in str(excinfo.value)

def test_service_validation_success(clean_env):
    """Test that QAService initializes correctly when keys are present."""
    with mock.patch("backend.app.core.config.settings.DEEPSEEK_API_KEY", "valid-key"):
        # Should not raise error
        service = QAService()
        assert service.llm_clients is not None
