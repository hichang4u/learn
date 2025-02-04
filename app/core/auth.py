from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging
import re

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# 로거 설정
logger = logging.getLogger(__name__)

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Bearer 토큰 형식 정규식
BEARER_TOKEN_PATTERN = re.compile(r'^Bearer [A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+$')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token_format(authorization: str) -> Optional[str]:
    """토큰 형식 검증"""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0] != "Bearer":
        return None
    
    token = parts[1]
    if not token or len(token.split()) > 1:  # 토큰에 공백이 있으면 안됨
        return None
    
    return token

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """현재 인증된 사용자 가져오기"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증에 실패했습니다.",
    )

    # 세션에서 user_id 확인
    user_id = request.session.get("user_id")
    if not user_id:
        logger.warning("세션에 user_id가 없음")
        raise credentials_exception

    # 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning(f"사용자를 찾을 수 없음: {user_id}")
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """현재 활성화된 사용자 가져오기"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 사용자입니다."
        )
    if not current_user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="승인되지 않은 사용자입니다."
        )
    return current_user 