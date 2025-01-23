from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """애플리케이션 설정"""
    SECRET_KEY: str = "your-secret-key-here"  # 실제 운영 환경에서는 안전한 키로 변경해야 함
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings() 