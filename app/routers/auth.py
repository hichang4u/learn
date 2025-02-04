from datetime import timedelta, datetime
from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.dependencies import get_db
from app.core.auth import create_access_token, get_current_user

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

@router.post("/login")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """로그인 처리"""
    logger.info(f"로그인 시도 - 이메일: {form_data.username}")
    logger.debug(f"요청 헤더: {dict(request.headers)}")
    
    try:
        user = crud.user.authenticate(
            db, 
            email=form_data.username,
            password=form_data.password
        )
        
        if not user:
            logger.warning(f"인증 실패 - 이메일: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )
        
        if not user.is_active:
            logger.warning(f"비활성 사용자 로그인 시도 - 이메일: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 사용자입니다."
            )

        if not user.is_approved:
            logger.warning(f"미승인 사용자 로그인 시도 - 이메일: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="관리자 승인 대기 중입니다."
            )

        # 세션에 사용자 정보 저장
        request.session["user_id"] = user.id
        request.session["role"] = "admin" if user.is_superuser else "user"
        logger.debug(f"세션 정보 저장 - user_id: {user.id}, role: {request.session['role']}")

        logger.info(f"로그인 성공 - 이메일: {form_data.username}")

        return {
            "user": schemas.UserResponse.from_orm(user)
        }

    except Exception as e:
        logger.error(f"로그인 처리 중 오류 발생 - 이메일: {form_data.username}", exc_info=True)
        raise

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    """현재 로그인한 사용자 정보 조회"""
    logger.debug(f"사용자 정보 조회 - 이메일: {current_user.email}")
    return current_user

@router.post("/logout")
async def logout(request: Request, response: Response):
    """로그아웃 처리"""
    logger.info(f"로그아웃 - user_id: {request.session.get('user_id')}")
    request.session.clear()
    return {"message": "로그아웃 성공"} 