from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from ..core import database
from .. import models, schemas, dependencies

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
            "password": account.hashed_password,
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
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    return account

@router.post("/", response_model=schemas.AccountResponse)
async def create_account(
    account: schemas.AccountCreate,
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    # 관리자만 계정 생성 가능
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 계정을 생성할 수 있습니다."
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
    
    # 계정 생성
    db_account = models.Account(
        platform_id=account.platform_id,
        email=account.email,
        hashed_password=account.password,
        memo=account.memo,
        is_active=account.is_active
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.put("/{account_id}")
async def update_account(
    account_id: int,
    account: schemas.AccountUpdate,
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    # 관리자만 계정 수정 가능
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 계정을 수정할 수 있습니다."
        )

    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    
    # 플랫폼 존재 여부 확인
    if account.platform_id:
        platform = db.query(models.Platform).filter(models.Platform.id == account.platform_id).first()
        if not platform:
            raise HTTPException(status_code=404, detail="존재하지 않는 플랫폼입니다.")
    
    # 다른 계정과 중복되는 이메일 체크
    if account.email:
        existing_account = db.query(models.Account).filter(
            models.Account.platform_id == (account.platform_id or db_account.platform_id),
            models.Account.email == account.email,
            models.Account.id != account_id
        ).first()
        if existing_account:
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    
    # 명시적으로 각 필드 업데이트
    if account.platform_id is not None:
        db_account.platform_id = account.platform_id
    if account.email is not None:
        db_account.email = account.email
    if account.password:  # 비밀번호가 제공된 경우에만 업데이트
        db_account.hashed_password = account.password
    if account.memo is not None:
        db_account.memo = account.memo
    if account.is_active is not None:
        db_account.is_active = account.is_active
    
    db.commit()
    db.refresh(db_account)
    
    # 응답 데이터 반환
    return {
        "id": db_account.id,
        "platform_id": db_account.platform_id,
        "email": db_account.email,
        "password": db_account.hashed_password,
        "memo": db_account.memo,
        "is_active": db_account.is_active,
        "created_at": db_account.created_at,
        "updated_at": db_account.updated_at,
        "platform": {
            "id": db_account.platform.id,
            "name": db_account.platform.name,
            "description": db_account.platform.description,
            "logo": db_account.platform.logo
        }
    }

@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    # 관리자만 계정 삭제 가능
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 계정을 삭제할 수 있습니다."
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