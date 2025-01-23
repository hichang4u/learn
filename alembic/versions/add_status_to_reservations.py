"""add status to reservations

Revision ID: add_status_to_reservations
Revises: 
Create Date: 2024-01-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.models.reservation import ReservationStatus

# revision identifiers, used by Alembic.
revision: str = 'add_status_to_reservations'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 예약 상태 enum 타입 생성
    reservation_status = sa.Enum(ReservationStatus, name='reservationstatus')
    reservation_status.create(op.get_bind(), checkfirst=True)
    
    # status 컬럼 추가
    op.add_column('reservations',
        sa.Column('status', 
                 reservation_status,
                 nullable=False,
                 server_default=ReservationStatus.PENDING.value)
    )

def downgrade() -> None:
    # status 컬럼 삭제
    op.drop_column('reservations', 'status')
    
    # enum 타입 삭제
    sa.Enum(name='reservationstatus').drop(op.get_bind(), checkfirst=True) 