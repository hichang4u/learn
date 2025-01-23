from datetime import datetime, date
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Date, ForeignKey, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class ReservationStatus(str, Enum):
    """예약 상태"""
    PENDING = "PENDING"      # 대기중
    APPROVED = "APPROVED"    # 승인됨
    REJECTED = "REJECTED"    # 거절됨
    IN_USE = "IN_USE"       # 사용중
    COMPLETED = "COMPLETED"  # 완료됨
    CANCELLED = "CANCELLED"  # 취소됨

class Reservation(Base):
    """예약 모델"""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    memo = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="reservations")
    account = relationship("Account", back_populates="reservations") 