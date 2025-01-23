from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from .. import models, schemas, database, auth, dependencies

router = APIRouter(
    prefix="/api/accounts",
    tags=["accounts"]
)

@router.get("/")
async def get_accounts(
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    platform_id: int | None = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Account)
    
    if platform_id is not None:
        query = query.filter(models.Account.platform_id == platform_id)
    
    accounts = query.order_by(models.Account.platform_id, models.Account.email).all()
    
    # 계정 정보를 딕셔너리로 직접 변환
    return [
        {
            "id": account.id,
            "platform_id": account.platform_id,
            "email": account.email,
            "memo": account.memo,
            "is_active": account.is_active,
            "created_at": account.created_at,
            "updated_at": account.updated_at,
            "platform": {
                "id": account.platform.id,
                "name": account.platform.name,
                "description": account.platform.description,
                "logo": account.platform.logo
            }
        }
        for account in accounts
    ]

@router.get("/{account_id}", response_model=schemas.AccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    return account

@router.post("/", response_model=schemas.AccountResponse)
async def create_account(
    account: schemas.AccountCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # 관리자만 계정 생성 가능
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    # 플랫폼 존재 여부 확인
    platform = db.query(models.Platform).filter(models.Platform.id == account.platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="존재하지 않는 플랫폼입니다.")
    
    # 이메일 중복 확인
    existing_account = db.query(models.Account).filter(
        models.Account.platform_id == account.platform_id,
        models.Account.email == account.email
    ).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    
    db_account = models.Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.put("/{account_id}", response_model=schemas.AccountResponse)
async def update_account(
    account_id: int,
    account: schemas.AccountUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # 관리자만 계정 수정 가능
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    
    # 플랫폼 존재 여부 확인
    platform = db.query(models.Platform).filter(models.Platform.id == account.platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="존재하지 않는 플랫폼입니다.")
    
    # 다른 계정과 중복되는 이메일 체크
    existing_account = db.query(models.Account).filter(
        models.Account.platform_id == account.platform_id,
        models.Account.email == account.email,
        models.Account.id != account_id
    ).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    
    for key, value in account.dict().items():
        setattr(db_account, key, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account

@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # 관리자만 계정 삭제 가능
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    
    # 예약 내역이 있는지 확인
    has_reservations = db.query(models.Reservation).filter(models.Reservation.account_id == account_id).first()
    if has_reservations:
        raise HTTPException(status_code=400, detail="이 계정에 연결된 예약 내역이 있어 삭제할 수 없습니다.")
    
    db.delete(account)
    db.commit()
    
    return {"message": "계정이 삭제되었습니다."} 