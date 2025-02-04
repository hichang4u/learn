import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app import models
from app.core.database import engine
from app.routers import accounts, auth, platforms, users, web, reservations, admin
from app.core.config import settings
from app.core.middleware import CSRFMiddleware

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# 세션 미들웨어 추가
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    max_age=settings.SESSION_MAX_AGE,  # 세션 유효기간 (초)
    same_site="lax",
    https_only=False  # 개발 환경에서는 False로 설정
)

# CSRF 미들웨어 추가
app.add_middleware(
    CSRFMiddleware,
    secret_key=settings.SECRET_KEY
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 초기화
models.Base.metadata.create_all(bind=engine)

# 정적 파일 설정
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# 라우터 설정
app.include_router(web)  # 웹 페이지 라우터
app.include_router(auth)  # 인증 API 라우터
app.include_router(users)  # 사용자 API 라우터
app.include_router(platforms)  # 플랫폼 API 라우터
app.include_router(accounts)  # 계정 API 라우터
app.include_router(reservations.router)  # 예약 API 라우터
app.include_router(admin.router)  # admin 라우터 추가

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Render에서 제공하는 PORT 환경 변수 사용, 로컬에서는 기본값 8000 사용
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)