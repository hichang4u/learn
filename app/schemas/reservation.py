from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, validator

from app.models.enums import ReservationStatus
from .user import UserResponse
from .account import AccountResponse

class ReservationBase(BaseModel):
    """예약 기본 스키마"""
    account_id: int
    start_date: date
    end_date: date
    status: ReservationStatus = ReservationStatus.PENDING
    memo: Optional[str] = None

class ReservationCreate(ReservationBase):
    """예약 생성 스키마"""
    account_id: int

class ReservationUpdate(BaseModel):
    """예약 수정 스키마"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    memo: Optional[str] = None
    status: Optional[ReservationStatus] = None

class ReservationResponse(ReservationBase):
    """예약 응답 스키마"""
    id: int
    user: UserResponse
    account: AccountResponse
    status: ReservationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @validator('status', pre=True)
    def normalize_status(cls, v):
        # DB에서 대문자로 저장된 상태 값을 소문자로 변환
        if isinstance(v, str):
            return v.lower()
        if hasattr(v, 'value'):
            return v.value.lower()
        return v

class ReservationStatusUpdate(BaseModel):
    """예약 상태 업데이트 스키마"""
    status: ReservationStatus
    memo: Optional[str] = None
    account_password: Optional[str] = None  # 승인 시 계정 비밀번호 