from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class Position(str, Enum):
    """사용자 직급"""
    STAFF = "STAFF"                           # 사원
    ASSISTANT_MANAGER = "ASSISTANT_MANAGER"    # 대리
    MANAGER = "MANAGER"                       # 과장
    DEPUTY_GENERAL_MANAGER = "DEPUTY_GENERAL_MANAGER"  # 차장
    GENERAL_MANAGER = "GENERAL_MANAGER"       # 부장
    DIRECTOR = "DIRECTOR"                     # 이사
    MANAGING_DIRECTOR = "MANAGING_DIRECTOR"   # 상무
    EXECUTIVE_DIRECTOR = "EXECUTIVE_DIRECTOR" # 전무
    CEO = "CEO"                              # 대표

class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    position = Column(SQLAlchemyEnum(Position), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan") 