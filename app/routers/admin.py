from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models import User, Reservation
from app.models.enums import ReservationStatus
from app.core.auth import get_current_active_user
from app.schemas import ReservationResponse

from app.dependencies import admin_required
from app.schemas.reservation import ReservationStatusUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/reservations", response_model=list[ReservationResponse])
async def get_reservations(
    current_user: Annotated[User, Depends(admin_required)],
    db: Session = Depends(get_db),
    status: Optional[ReservationStatus] = None
):
    """관리자용 예약 목록 조회 API"""
    query = db.query(Reservation)
    
    if status:
        query = query.filter(Reservation.status == status)
    
    # 최신순으로 정렬
    query = query.order_by(Reservation.created_at.desc())
    
    return query.all()

@router.put("/reservations/{reservation_id}/status")
async def update_reservation_status(
    reservation_id: int,
    update_data: ReservationStatusUpdate,
    current_user: Annotated[User, Depends(admin_required)],
    db: Session = Depends(get_db)
):
    """예약 상태 업데이트 API"""
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="예약을 찾을 수 없습니다."
        )
    
    # 승인 시 비밀번호 필수 체크
    if update_data.status == ReservationStatus.APPROVED and not update_data.account_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="승인 시에는 계정 비밀번호를 입력해야 합니다."
        )
    
    # 상태 업데이트
    reservation.status = update_data.status
    
    # 메모 업데이트
    if update_data.status == ReservationStatus.APPROVED:
        # 승인 시 메모에 계정 정보 추가
        memo_parts = []
        if update_data.memo:
            memo_parts.append(update_data.memo)
        memo_parts.append(f"계정 비밀번호: {update_data.account_password}")
        reservation.memo = "\n".join(memo_parts)
    elif update_data.memo:
        reservation.memo = update_data.memo
    
    db.commit()
    return {"message": "상태가 업데이트되었습니다."} 