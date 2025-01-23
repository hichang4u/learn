from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import UserRole

# Platform 스키마
class PlatformBase(BaseModel):
    """플랫폼 기본 스키마"""
    name: str
    url: str
    logo: Optional[str] = None
    description: Optional[str] = None

class PlatformCreate(PlatformBase):
    """플랫폼 생성 스키마"""
    pass

class PlatformUpdate(PlatformBase):
    """플랫폼 수정 스키마"""
    pass

class PlatformResponse(PlatformBase):
    """플랫폼 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Account 스키마
class AccountBase(BaseModel):
    platform_id: int
    email: str
    password: str
    memo: Optional[str] = None
    is_active: bool = True

class AccountCreate(AccountBase):
    pass

class AccountUpdate(AccountBase):
    pass

class AccountResponse(BaseModel):
    id: int
    platform_id: int
    email: str
    memo: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# User 스키마
class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str
    email: str
    phone: Optional[str] = None
    position: Optional[str] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str

class UserUpdate(UserBase):
    """사용자 수정 스키마"""
    password: str

class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 