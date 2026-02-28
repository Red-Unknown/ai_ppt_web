from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "FWWB A12 AI Interactive Course System"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Logging Configuration
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_SIZE: int = 10  # MB
    LOG_BACKUP_COUNT: int = 5
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fwwb_a12"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # DeepSeek Configuration
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 2048
    DEEPSEEK_TEMPERATURE: float = 0.7
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_PROMPTS_PATH: str = "backend/app/core/prompts/qa_prompts.json"
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
