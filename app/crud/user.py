from typing import Optional
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import User

def authenticate(db: Session, *, email: str, password: str) -> Optional[User]:
    """사용자 인증"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get(db: Session, user_id: int) -> Optional[User]:
    """사용자 조회"""
    return db.query(User).filter(User.id == user_id).first() 