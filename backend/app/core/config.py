from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

# Calculate Project Root
# backend/app/core/config.py -> backend/app/core -> backend/app -> backend -> project_root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "FWWB A12 AI Interactive Course System"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    ALLOWED_HOSTS: List[str] = ["*"]

    # Paths
    BASE_DIR: Path = PROJECT_ROOT
    
    # Logging Configuration
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_SIZE: int = 1  # MB
    LOG_BACKUP_COUNT: int = 5
    LOG_DIR: Path = PROJECT_ROOT / "log"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:yaoshun2006@10.0.0.4:5432/A12database"
    
    # Redis
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

    # Feature Flags
    ENABLE_SUGGESTIONS: bool = True


    class Config:
        env_file = ".env"

settings = Settings()
