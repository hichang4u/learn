from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app import models
from app.database import engine
from app.routers import accounts, auth, platforms, users, web, reservations, admin
from app.core.config import settings

app = FastAPI(
    title="학습 계정 관리 시스템",
    description="다양한 온라인 강의 플랫폼의 계정을 관리하는 시스템입니다."
)

# 세션 미들웨어 추가
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    max_age=3600,  # 1시간
    same_site="lax",
    https_only=True
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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