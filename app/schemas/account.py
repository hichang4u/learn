from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class AccountBase(BaseModel):
    """계정 기본 스키마"""
    platform_id: int
    email: EmailStr
    memo: Optional[str] = None
    is_active: bool = True

class AccountCreate(BaseModel):
    """계정 생성 스키마"""
    platform_id: int
    email: str
    password: str
    memo: Optional[str] = None
    is_active: bool = True

class AccountUpdate(BaseModel):
    """계정 수정 스키마"""
    platform_id: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None
    memo: Optional[str] = None
    is_active: Optional[bool] = None

class AccountResponse(BaseModel):
    """계정 응답 스키마"""
    id: int
    platform_id: int
    email: str
    hashed_password: str  # 비밀번호 표시를 위해 추가
    memo: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    platform: 'PlatformResponse'

    class Config:
        from_attributes = True

from .platform import PlatformResponse  # 순환 참조 방지를 위해 클래스 정의 후 import 