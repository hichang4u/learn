from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.dependencies import get_db

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)]
) -> models.User:
    """현재 인증된 사용자 조회"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증되지 않은 사용자입니다."
        )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = int(payload["sub"])
    except (jwt.JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 정보입니다."
        )
    
    user = crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    return user

async def verify_session(request: Request):
    """세션 검증"""
    # 세션 만료 시간 검증
    expiry = request.session.get("expiry")
    if expiry:
        expiry_time = datetime.fromisoformat(expiry)
        if datetime.now() > expiry_time:
            request.session.clear()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="세션이 만료되었습니다. 다시 로그인해주세요."
            )
    
    # IP 검증
    if "client_ip" in request.session:
        stored_ip = request.session["client_ip"]
        current_ip = request.client.host
        
        # IP가 변경된 경우
        if stored_ip != current_ip:
            request.session.clear()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="보안을 위해 다시 로그인해주세요."
            )
    
    # 마지막 활동 시간 검증
    last_activity = request.session.get("last_activity")
    if last_activity:
        last_activity = datetime.fromisoformat(last_activity)
        idle_time = datetime.now() - last_activity
        
        # 30분 이상 비활성 상태인 경우
        if idle_time > timedelta(minutes=30):
            request.session.clear()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="장시간 활동이 없어 로그아웃되었습니다."
            )
    
    # 현재 시간을 마지막 활동 시간으로 업데이트
    request.session["last_activity"] = datetime.now().isoformat()

@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember_me: bool = Form(False),
    db: Session = Depends(get_db)
):
    """로그인 처리"""
    user = crud.user.authenticate(
        db, 
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    
    # 세션에 사용자 정보 저장
    session_data = {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": "admin" if user.is_superuser else "user",
        "position": user.position.name.upper() if user.position else None,
        "position_value": user.position.value if user.position else None,
        "is_active": True,
        "last_login": datetime.now().isoformat(),
        "session_id": security.create_random_string(),
        "client_ip": request.client.host,
        "expiry": (datetime.now() + timedelta(days=30 if remember_me else 1)).isoformat()
    }
    
    request.session.update(session_data)
    
    return {"message": "로그인 성공"}

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    """현재 로그인한 사용자 정보 조회"""
    return current_user

@router.post("/logout")
async def logout(request: Request):
    """로그아웃 처리"""
    request.session.clear()
    return {"message": "로그아웃 성공"} 