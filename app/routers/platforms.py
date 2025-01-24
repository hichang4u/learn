from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
import logging
from .. import models, schemas, database, dependencies, crud

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/platforms",
    tags=["platforms"]
)

@router.get("/", response_model=List[schemas.PlatformResponse])
async def get_platforms(
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    logger.info(f"플랫폼 목록 조회 요청 - 사용자: {current_user.email}")
    platforms = db.query(models.Platform).order_by(models.Platform.name).all()
    
    # 플랫폼 데이터 로깅
    for platform in platforms:
        logger.info(f"플랫폼 정보: id={platform.id}, name={platform.name}, description={platform.description}")
    
    logger.info(f"총 {len(platforms)}개의 플랫폼이 조회됨")
    return platforms

@router.get("/{platform_id}", response_model=schemas.PlatformResponse)
async def get_platform(
    platform_id: int,
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    platform = db.query(models.Platform).filter(models.Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="플랫폼을 찾을 수 없습니다.")
    return platform

@router.post("/", response_model=schemas.PlatformResponse)
async def create_platform(
    platform: schemas.PlatformCreate,
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    # 관리자만 플랫폼을 생성할 수 있음
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="관리자만 플랫폼을 생성할 수 있습니다."
        )
    
    # 중복 이름 체크
    existing = db.query(models.Platform).filter(models.Platform.name == platform.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 플랫폼 이름입니다.")
    
    return crud.platform.create(db, obj_in=platform)

@router.put("/{platform_id}", response_model=schemas.PlatformResponse)
async def update_platform(
    platform_id: int,
    platform: schemas.PlatformUpdate,
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    # 관리자만 플랫폼 수정 가능
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 플랫폼을 수정할 수 있습니다."
        )

    db_platform = db.query(models.Platform).filter(models.Platform.id == platform_id).first()
    if not db_platform:
        raise HTTPException(status_code=404, detail="플랫폼을 찾을 수 없습니다.")
    
    # 다른 플랫폼과 중복되는 이름 체크
    existing = db.query(models.Platform).filter(
        models.Platform.name == platform.name,
        models.Platform.id != platform_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 플랫폼 이름입니다.")
    
    for key, value in platform.dict().items():
        setattr(db_platform, key, value)
    
    db.commit()
    db.refresh(db_platform)
    return db_platform

@router.delete("/{platform_id}")
async def delete_platform(
    platform_id: int,
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    # 관리자만 플랫폼 삭제 가능
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 플랫폼을 삭제할 수 있습니다."
        )

    platform = db.query(models.Platform).filter(models.Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="플랫폼을 찾을 수 없습니다.")
    
    # 연결된 계정이 있는지 확인
    has_accounts = db.query(models.Account).filter(models.Account.platform_id == platform_id).first()
    if has_accounts:
        raise HTTPException(status_code=400, detail="이 플랫폼에 연결된 계정이 있어 삭제할 수 없습니다.")
    
    db.delete(platform)
    db.commit()
    
    return {"message": "플랫폼이 삭제되었습니다."} 