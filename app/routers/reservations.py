from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from datetime import datetime
from .. import models, schemas, database, dependencies
from ..schemas.reservation import ReservationCreate, ReservationResponse
from ..models.reservation import ReservationStatus

router = APIRouter(
    prefix="/api/reservations",
    tags=["reservations"]
)

@router.post("/", response_model=ReservationResponse)
async def create_reservation(
    reservation: ReservationCreate,
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    """새로운 예약 생성"""
    # 이미 진행 중인 예약이 있는지 확인
    active_reservation = db.query(models.Reservation).filter(
        models.Reservation.user_id == current_user.id,
        models.Reservation.status.in_([
            ReservationStatus.PENDING,
            ReservationStatus.APPROVED,
            ReservationStatus.IN_USE
        ])
    ).first()
    
    if active_reservation:
        raise HTTPException(
            status_code=400,
            detail="이미 진행 중인 예약이 있습니다. 새로운 예약은 현재 예약이 완료된 후에 가능합니다."
        )

    # 계정이 존재하는지 확인
    account = db.query(models.Account).filter(models.Account.id == reservation.account_id).first()
    if not account:
        raise HTTPException(
            status_code=404,
            detail="계정을 찾을 수 없습니다."
        )

    # 계정이 사용 가능한지 확인
    if not account.is_active:
        raise HTTPException(status_code=400, detail="이미 사용 중인 계정입니다.")
    
    # 날짜 유효성 검사
    if reservation.start_date > reservation.end_date:
        raise HTTPException(status_code=400, detail="종료일이 시작일보다 빠를 수 없습니다.")
    
    # 기간이 1달을 초과하는지 확인
    if (reservation.end_date - reservation.start_date).days > 30:
        raise HTTPException(status_code=400, detail="예약 기간은 1달을 초과할 수 없습니다.")
    
    # 해당 기간에 이미 예약이 있는지 확인
    existing_reservation = db.query(models.Reservation).filter(
        models.Reservation.account_id == reservation.account_id,
        models.Reservation.status.notin_([ReservationStatus.CANCELLED, ReservationStatus.REJECTED]),
        models.Reservation.start_date <= reservation.end_date,
        models.Reservation.end_date >= reservation.start_date
    ).first()
    
    if existing_reservation:
        raise HTTPException(status_code=400, detail="해당 기간에 이미 예약이 존재합니다.")
    
    # 예약 생성
    db_reservation = models.Reservation(
        user_id=current_user.id,
        account_id=reservation.account_id,
        start_date=reservation.start_date,
        end_date=reservation.end_date,
        memo=reservation.memo,
        status=ReservationStatus.PENDING
    )
    
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    
    return db_reservation

@router.get("/", response_model=List[ReservationResponse])
async def get_reservations(
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    """사용자의 예약 목록 조회"""
    reservations = db.query(models.Reservation).filter(
        models.Reservation.user_id == current_user.id
    ).order_by(models.Reservation.created_at.desc()).all()
    
    return reservations

@router.get("/check")
async def check_reservation(
    platform_id: int,
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    """사용자의 플랫폼 계정 예약 가능 여부 체크"""
    # 사용 가능한 계정이 있는지 확인
    available_accounts = db.query(models.Account).filter(
        models.Account.platform_id == platform_id,
        models.Account.is_active == True
    ).all()

    return {
        "has_available_accounts": len(available_accounts) > 0,
        "available_accounts": [schemas.AccountResponse.from_orm(account) for account in available_accounts]
    }

@router.get("/approved", response_model=List[ReservationResponse])
async def get_approved_reservations(
    current_user: Annotated[models.User, Depends(dependencies.login_required)],
    db: Session = Depends(database.get_db)
):
    """승인된 예약 목록 조회"""
    reservations = db.query(models.Reservation).filter(
        models.Reservation.status.in_([
            ReservationStatus.APPROVED,
            ReservationStatus.IN_USE
        ])
    ).order_by(models.Reservation.start_date.asc()).all()
    
    return reservations 