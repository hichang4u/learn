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
    position_value: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.position:
            # position에 따른 한글 직급 설정
            position_map = {
                Position.STAFF: "사원",
                Position.ASSISTANT_MANAGER: "대리",
                Position.MANAGER: "과장",
                Position.DEPUTY_GENERAL_MANAGER: "차장",
                Position.GENERAL_MANAGER: "부장",
                Position.DIRECTOR: "이사",
                Position.MANAGING_DIRECTOR: "상무",
                Position.EXECUTIVE_DIRECTOR: "전무",
                Position.CEO: "대표"
            }
            self.position_value = position_map.get(self.position) 