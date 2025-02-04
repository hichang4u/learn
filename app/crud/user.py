import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.models import User
from app import schemas

# 로깅 설정
logger = logging.getLogger(__name__)

def authenticate(db: Session, *, email: str, password: str) -> Optional[User]:
    """사용자 인증"""
    user = get_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get(db: Session, user_id: int) -> Optional[User]:
    """사용자 조회"""
    return db.query(User).filter(User.id == user_id).first()

def get_by_email(db: Session, email: str) -> Optional[User]:
    """이메일로 사용자 조회"""
    return db.query(User).filter(User.email == email).first()

def get_all(db: Session, skip: int = 0, limit: int = 100):
    """모든 사용자 조회"""
    return db.query(User).offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: schemas.UserCreate) -> User:
    """사용자 생성"""
    try:
        logger.info(f"사용자 생성 시작 - 이메일: {obj_in.email}")
        
        # 이메일 중복 체크
        if get_by_email(db, email=obj_in.email):
            logger.error(f"이메일 중복 - {obj_in.email}")
            raise ValueError("이미 등록된 이메일입니다.")
        
        # 사용자 객체 생성
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            position=obj_in.position,
            is_active=obj_in.is_active,
            is_approved=obj_in.is_approved,
            is_superuser=obj_in.is_superuser
        )
        logger.info("User 객체 생성 완료")
        
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"사용자 생성 성공 - ID: {db_obj.id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"DB 저장 실패: {str(e)}")
            raise ValueError("사용자 저장 중 오류가 발생했습니다.") from e
            
    except Exception as e:
        logger.error(f"사용자 생성 실패: {str(e)}")
        raise

def update(db: Session, *, db_obj: User, obj_in: schemas.UserUpdate) -> User:
    """사용자 정보 업데이트"""
    update_data = obj_in.dict(exclude_unset=True)
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, *, user_id: int) -> Optional[User]:
    """사용자 삭제"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user