from datetime import datetime, date
from app.models.enums import ReservationStatus

from sqlalchemy import Boolean, Column, DateTime, Date, ForeignKey, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

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