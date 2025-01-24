from sqlalchemy.orm import Session
from .. import models, schemas

def create(db: Session, *, obj_in: schemas.PlatformCreate) -> models.Platform:
    """플랫폼 생성"""
    db_obj = models.Platform(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get(db: Session, id: int) -> models.Platform:
    """ID로 플랫폼 조회"""
    return db.query(models.Platform).filter(models.Platform.id == id).first()

def get_by_name(db: Session, name: str) -> models.Platform:
    """이름으로 플랫폼 조회"""
    return db.query(models.Platform).filter(models.Platform.name == name).first()

def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> list[models.Platform]:
    """플랫폼 목록 조회"""
    return db.query(models.Platform).offset(skip).limit(limit).all()

def update(db: Session, *, db_obj: models.Platform, obj_in: schemas.PlatformUpdate) -> models.Platform:
    """플랫폼 수정"""
    for field, value in obj_in.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, *, id: int) -> models.Platform:
    """플랫폼 삭제"""
    obj = db.query(models.Platform).get(id)
    db.delete(obj)
    db.commit()
    return obj 