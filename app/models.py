from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class Platform(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정
    accounts = relationship("Account", back_populates="platform")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id", ondelete="RESTRICT"), nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    memo = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 플랫폼별 이메일 유니크 제약조건
    __table_args__ = (
        UniqueConstraint('platform_id', 'email', name='uix_platform_email'),
    )

    # 관계 설정
    platform = relationship("Platform", back_populates="accounts")
    reservations = relationship("Reservation", back_populates="account")

class UserRole(str, enum.Enum):
    """사용자 역할"""
    ADMIN = "admin"
    USER = "user"

class Position(enum.Enum):
    STAFF = "사원"
    ASSISTANT_MANAGER = "대리"
    MANAGER = "과장"
    DEPUTY_GENERAL_MANAGER = "차장"
    GENERAL_MANAGER = "부장"
    DIRECTOR = "이사"
    MANAGING_DIRECTOR = "상무"
    EXECUTIVE_DIRECTOR = "전무"
    CEO = "대표"

class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    position = Column(Enum(Position), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정
    reservations = relationship("Reservation", back_populates="user")

class ReservationStatus(str, enum.Enum):
    """예약 상태"""
    PENDING = "PENDING"  # 대기중
    APPROVED = "APPROVED"  # 승인됨
    REJECTED = "REJECTED"  # 거절됨
    IN_USE = "IN_USE"  # 사용중
    COMPLETED = "COMPLETED"  # 완료됨
    CANCELLED = "CANCELLED"  # 취소됨

class Reservation(Base):
    """예약 모델"""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False)
    memo = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정
    user = relationship("User", back_populates="reservations")
    account = relationship("Account", back_populates="reservations") 