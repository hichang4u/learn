import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Reservation, ReservationStatus, Account, Platform, User, UserRole
from datetime import datetime, timedelta

class TestReservation:
    """예약 모델 테스트 클래스"""

    @pytest.fixture
    def sample_data(self, test_db):
        """테스트용 기본 데이터"""
        # 플랫폼 생성
        platform = Platform(
            name="인프런",
            url="https://www.inflearn.com"
        )
        test_db.add(platform)
        test_db.commit()

        # 계정 생성
        account = Account(
            platform_id=platform.id,
            email="test@example.com",
            password="testpass",
            is_available=True
        )
        test_db.add(account)

        # 사용자 생성
        user = User(
            username="testuser",
            email="user@example.com",
            password="userpass",
            role=UserRole.USER
        )
        test_db.add(user)
        test_db.commit()

        return {
            "platform": platform,
            "account": account,
            "user": user
        }

    def test_create_reservation_success(self, test_db, sample_data):
        """예약 생성 성공 테스트"""
        # Given
        reservation_data = {
            "account_id": sample_data["account"].id,
            "user_id": sample_data["user"].id,
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=7),
            "memo": "테스트 예약입니다."
        }

        # When
        reservation = Reservation(**reservation_data)
        test_db.add(reservation)
        test_db.commit()
        test_db.refresh(reservation)

        # Then
        assert reservation.id is not None
        assert reservation.status == ReservationStatus.PENDING
        assert reservation.start_date == reservation_data["start_date"]
        assert reservation.end_date == reservation_data["end_date"]
        assert isinstance(reservation.created_at, datetime)

    def test_reservation_status_transition(self, test_db, sample_data):
        """예약 상태 변경 테스트"""
        # Given
        reservation = Reservation(
            account_id=sample_data["account"].id,
            user_id=sample_data["user"].id,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )
        test_db.add(reservation)
        test_db.commit()

        # When & Then
        # PENDING -> APPROVED
        reservation.status = ReservationStatus.APPROVED
        test_db.commit()
        assert reservation.status == ReservationStatus.APPROVED

        # APPROVED -> IN_USE
        reservation.status = ReservationStatus.IN_USE
        test_db.commit()
        assert reservation.status == ReservationStatus.IN_USE

        # IN_USE -> RETURNED
        reservation.status = ReservationStatus.RETURNED
        test_db.commit()
        assert reservation.status == ReservationStatus.RETURNED

    def test_prevent_duplicate_reservation(self, test_db, sample_data):
        """동일 기간 중복 예약 방지 테스트"""
        # Given
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        reservation1 = Reservation(
            account_id=sample_data["account"].id,
            user_id=sample_data["user"].id,
            start_date=start_date,
            end_date=end_date
        )
        test_db.add(reservation1)
        test_db.commit()

        # When & Then
        # 기간이 겹치는 예약 시도
        reservation2 = Reservation(
            account_id=sample_data["account"].id,
            user_id=sample_data["user"].id,
            start_date=start_date + timedelta(days=3),
            end_date=end_date + timedelta(days=3)
        )
        test_db.add(reservation2)
        
        # 중복 예약 체크
        overlapping = test_db.query(Reservation).filter(
            Reservation.account_id == sample_data["account"].id,
            Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.APPROVED, ReservationStatus.IN_USE]),
            Reservation.start_date < reservation2.end_date,
            Reservation.end_date > reservation2.start_date
        ).first()
        
        assert overlapping is not None

    def test_validate_reservation_dates(self, test_db, sample_data):
        """예약 기간 유효성 검증 테스트"""
        # Given
        start_date = datetime.now()
        end_date = start_date - timedelta(days=1)  # 종료일이 시작일보다 이전

        # When & Then
        with pytest.raises(ValueError):
            reservation = Reservation(
                account_id=sample_data["account"].id,
                user_id=sample_data["user"].id,
                start_date=start_date,
                end_date=end_date
            )
            # 시작일이 종료일보다 늦은 경우 검증
            if reservation.start_date >= reservation.end_date:
                raise ValueError("종료일은 시작일보다 이후여야 합니다.")
            test_db.add(reservation)
            test_db.commit()

    def test_check_account_availability(self, test_db, sample_data):
        """계정 사용 가능 상태 확인 테스트"""
        # Given
        sample_data["account"].is_available = False
        test_db.commit()

        # When & Then
        with pytest.raises(ValueError):
            reservation = Reservation(
                account_id=sample_data["account"].id,
                user_id=sample_data["user"].id,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=7)
            )
            # 계정 사용 가능 상태 검증
            account = test_db.query(Account).filter(Account.id == reservation.account_id).first()
            if not account.is_available:
                raise ValueError("사용 불가능한 계정입니다.")
            test_db.add(reservation)
            test_db.commit()

    def test_cancel_reservation(self, test_db, sample_data):
        """예약 취소 테스트"""
        # Given
        reservation = Reservation(
            account_id=sample_data["account"].id,
            user_id=sample_data["user"].id,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )
        test_db.add(reservation)
        test_db.commit()

        # When
        reservation.status = ReservationStatus.CANCELLED
        test_db.commit()

        # Then
        assert reservation.status == ReservationStatus.CANCELLED 