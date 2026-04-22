from pydantic_settings import BaseSettings
from typing import List, Dict, Any
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

class Settings(BaseSettings):
    PROJECT_NAME: str = "FWWB A12 AI Interactive Course System"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    ALLOWED_HOSTS: List[str] = ["*"]

    BASE_DIR: Path = PROJECT_ROOT
    
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_SIZE: int = 1
    LOG_BACKUP_COUNT: int = 5
    LOG_DIR: Path = PROJECT_ROOT / "log"
    
    DB_CONFIG: Dict[str, Any] = {
        "host": "10.0.0.4",
        "port": 5432,
        "user": "postgres",
        "password": "yaoshun2006",
        "timeout": 30,
        "connect_timeout": 30,
        "ssl": False,
    }
    
    TARGET_DB: str = "ai_ppt_web"
    
    REDIS_URL: str = "redis://localhost:6379/0"

    # DeepSeek Configuration
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_REASONER_MODEL: str = "deepseek-reasoner"
    DEEPSEEK_MAX_TOKENS: int = 10000
    DEEPSEEK_TEMPERATURE: float = 0.7
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_PROMPTS_PATH: Path = PROJECT_ROOT / "backend/app/core/prompts/qa_prompts.json"
    OPENAI_API_KEY: str = ""

    # Web Search Configuration
    TAVILY_API_KEY: str = ""

    # Kimi Configuration (for built-in web search)
    KIMI_API_KEY: str = ""
    KIMI_BASE_URL: str = "https://api.moonshot.cn/v1"
    KIMI_MODEL: str = "moonshot-v1-8k"
    KIMI_MAX_TOKENS: int = 8000
    KIMI_TEMPERATURE: float = 0.7

    # Qwen Configuration (Alibaba Cloud)
    QWEN_API_KEY: str = ""
    DASHSCOPE_API_KEY: str = ""
    QWEN_MODEL: str = "qwen-turbo"
    QWEN_VISION_MODEL: str = "qwen-vl-plus"
    QWEN_MAX_TOKENS: int = 2000
    QWEN_TEMPERATURE: float = 0.7
    QWEN_BASE_URL: str = DEFAULT_DASHSCOPE_BASE_URL
    DASHSCOPE_BASE_URL: str = DEFAULT_DASHSCOPE_BASE_URL
    IMAGE_VLM_API_KEY: str = ""
    IMAGE_VLM_BASE_URL: str = ""
    IMAGE_VLM_MODEL: str = ""

    # Feature Flags
    ENABLE_SUGGESTIONS: bool = True


    class Config:
        env_file = ".env"
        extra = "ignore"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Force .env values to take priority over shell/system env vars.
        return init_settings, dotenv_settings, env_settings, file_secret_settings

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_CONFIG.get("host"):
            return f"postgresql+asyncpg://{self.DB_CONFIG['user']}:{self.DB_CONFIG['password']}@{self.DB_CONFIG['host']}:{self.DB_CONFIG['port']}/{self.TARGET_DB}"
        return ""

    @property
    def EFFECTIVE_QWEN_API_KEY(self) -> str:
        return self.QWEN_API_KEY or self.DASHSCOPE_API_KEY

    @property
    def EFFECTIVE_QWEN_BASE_URL(self) -> str:
        def _is_valid_dashscope_api_url(url: str) -> bool:
            candidate = (url or "").strip().rstrip("/")
            if not candidate:
                return False
            parsed = urlparse(candidate)
            host = (parsed.netloc or "").lower()
            path = (parsed.path or "").lower()
            if "console.aliyun.com" in host:
                return False
            if not host.endswith("aliyuncs.com"):
                return False
            if "/compatible-mode/" not in path:
                return False
            return True

        for candidate in (
            self.QWEN_BASE_URL,
            self.DASHSCOPE_BASE_URL,
            DEFAULT_DASHSCOPE_BASE_URL,
        ):
            normalized = (candidate or "").strip().rstrip("/")
            if _is_valid_dashscope_api_url(normalized):
                return normalized

        raise ValueError(
            "No valid DashScope compatible API base URL found. "
            "Please set QWEN_BASE_URL or DASHSCOPE_BASE_URL to "
            "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    @property
    def EFFECTIVE_IMAGE_VLM_API_KEY(self) -> str:
        return self.IMAGE_VLM_API_KEY or self.EFFECTIVE_QWEN_API_KEY

    @property
    def EFFECTIVE_IMAGE_VLM_BASE_URL(self) -> str:
        return (self.IMAGE_VLM_BASE_URL or "").strip().rstrip("/") or self.EFFECTIVE_QWEN_BASE_URL

    @property
    def EFFECTIVE_IMAGE_VLM_MODEL(self) -> str:
        return self.IMAGE_VLM_MODEL or self.QWEN_VISION_MODEL

settings = Settings()
