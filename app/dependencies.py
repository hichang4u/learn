"""
# 의존성 주입 관련 프로젝트 규칙

## 1. 데이터베이스 세션 관리
- 모든 요청에서 새로운 세션 생성
- 요청 종료 시 자동으로 세션 닫기
- 트랜잭션 자동 롤백 (예외 발생 시)

## 2. 사용자 인증 의존성
### 2.1 get_current_user_or_none
- 세션에서 user_id 확인
- 로그인하지 않은 경우 None 반환
- 비활성 사용자는 None 반환
- 실제 사용자 객체 반환

### 2.2 login_required
- API 요청: 401 Unauthorized 반환
- 웹 페이지: /login으로 리다이렉트
- 활성 사용자만 접근 가능

### 2.3 admin_required
- 로그인 필수
- 관리자 권한 확인
- 권한 없는 경우 403 Forbidden
- 세션의 role이 'admin'인지 확인

## 3. 에러 처리
- 401: 인증되지 않은 사용자
- 403: 권한 없는 사용자
- 307: 로그인 페이지로 리다이렉트

## 4. 보안 규칙
- 세션 기반 인증
- CSRF 토큰 검증
- 관리자 권한 엄격한 검증
"""

from typing import Annotated, Generator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import crud, models
from app.core.database import SessionLocal

def get_db() -> Generator:
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user_or_none(
    request: Request,
    db: Annotated[Session, Depends(get_db)]
) -> Optional[models.User]:
    """현재 로그인한 사용자 정보를 반환하거나 None을 반환"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = crud.user.get(db, user_id)
    if not user or not user.is_active:
        return None
        
    return user

async def login_required(
    request: Request,
    user: Annotated[Optional[models.User], Depends(get_current_user_or_none)]
) -> models.User:
    """로그인이 필요한 페이지에서 사용하는 의존성"""
    if not user:
        if request.url.path.startswith("/api/"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="로그인이 필요합니다."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/login"}
            )
    return user

async def admin_required(
    request: Request,
    user: Annotated[Optional[models.User], Depends(get_current_user_or_none)]
) -> models.User:
    """관리자 권한이 필요한 엔드포인트에서 사용하는 의존성"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )
    
    if not user.is_superuser:  # session의 role 대신 user 모델의 is_superuser 사용
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    
    return user 