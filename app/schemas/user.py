from __future__ import annotations
from datetime import datetime
from typing import Optional, Annotated, TypeAlias
from pydantic import BaseModel, EmailStr, Field, validator, constr, field_serializer
import re

from app.models.enums import Position

# Define constrained types using Annotated
FullNameStr = Annotated[str, constr(min_length=1)]
PasswordStr = Annotated[str, constr(min_length=8)]

class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr
    full_name: FullNameStr
    position: Position = Position.STAFF
    is_active: bool = True
    is_approved: bool = False

    @validator("is_approved", pre=True, always=True)
    def convert_is_approved(cls, v):
        if isinstance(v, int):
            return bool(v)
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError('이름은 필수입니다.')
        return v.strip()

class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: PasswordStr

class UserUpdate(BaseModel):
    """사용자 수정 스키마"""
    full_name: Optional[FullNameStr] = None
    position: Optional[Position] = None
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None
    password: Optional[PasswordStr] = None

    @validator("password")
    def validate_password(cls, v):
        if v is None:
            return v
        if not any(c.isupper() for c in v):
            raise ValueError("비밀번호는 최소 1개의 대문자를 포함해야 합니다")
        if not any(c.islower() for c in v):
            raise ValueError("비밀번호는 최소 1개의 소문자를 포함해야 합니다")
        if not any(c.isdigit() for c in v):
            raise ValueError("비밀번호는 최소 1개의 숫자를 포함해야 합니다")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("비밀번호는 최소 1개의 특수문자를 포함해야 합니다")
        return v

class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

    @field_serializer("is_approved")
    def serialize_is_approved(self, v, info):
        return bool(v)