from typing import Annotated, Generator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import crud, models
from app.database import SessionLocal

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
    
    if request.session.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    
    return user 