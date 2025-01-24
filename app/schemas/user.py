from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models import Position

class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr
    full_name: str
    position: Optional[Position] = None

class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str

class UserUpdate(BaseModel):
    """사용자 수정 스키마"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    position: Optional[Position] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """사용자 응답 스키마"""
    id: int
    email: str
    full_name: str
    position: Optional[Position] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True