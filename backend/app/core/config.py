from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "FWWB A12 AI Interactive Course System"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fwwb_a12"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"

settings = Settings()
