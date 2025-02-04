from pydantic_settings import BaseSettings
from typing import List
import secrets

class Settings(BaseSettings):
    """애플리케이션 설정"""
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI 프로젝트 템플릿"
    
    # 보안 설정
    SECRET_KEY: str = "your-super-secret-key-here"  # 실제 운영 환경에서는 환경 변수로 설정해야 합니다
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./learn.db"
    
    # CORS 설정
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # 세션 설정
    SESSION_MAX_AGE: int = 3600  # 1시간
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 