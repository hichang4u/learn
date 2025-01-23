from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel

from app.models import ReservationStatus
from .user import UserResponse
from .account import AccountResponse

class ReservationBase(BaseModel):
    """예약 기본 스키마"""
    start_date: date
    end_date: date
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

class ReservationStatusUpdate(BaseModel):
    """예약 상태 업데이트 스키마"""
    status: ReservationStatus
    memo: Optional[str] = None
    account_password: Optional[str] = None  # 승인 시 계정 비밀번호 