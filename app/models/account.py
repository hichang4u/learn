from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Account(Base):
    """계정 모델"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    email = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    memo = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    platform = relationship("Platform", back_populates="accounts")
    reservations = relationship("Reservation", back_populates="account", cascade="all, delete-orphan") 