from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class AccountBase(BaseModel):
    """계정 기본 스키마"""
    platform_id: int
    email: EmailStr
    memo: Optional[str] = None
    is_active: bool = True

class AccountCreate(AccountBase):
    """계정 생성 스키마"""
    password: str

class AccountUpdate(AccountBase):
    """계정 수정 스키마"""
    platform_id: Optional[int] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class AccountResponse(BaseModel):
    """계정 응답 스키마"""
    id: int
    platform_id: int
    email: str
    memo: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    platform: 'PlatformResponse'

    class Config:
        from_attributes = True

from .platform import PlatformResponse  # 순환 참조 방지를 위해 클래스 정의 후 import 