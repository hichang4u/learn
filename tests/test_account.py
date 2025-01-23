import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Account, Platform, User, UserRole
from datetime import datetime

class TestAccount:
    """계정 모델 테스트 클래스"""

    @pytest.fixture
    def sample_platform(self, test_db):
        """테스트용 플랫폼 데이터"""
        platform = Platform(
            name="인프런",
            url="https://www.inflearn.com",
            logo="https://www.inflearn.com/logo.png",
            description="온라인 강의 플랫폼"
        )
        test_db.add(platform)
        test_db.commit()
        test_db.refresh(platform)
        return platform

    def test_create_account_success(self, test_db, sample_platform):
        """계정 생성 성공 테스트"""
        account_data = {
            "platform_id": sample_platform.id,
            "email": "platform@example.com",
            "password": "platformpass123",
            "memo": "테스트 계정입니다."
        }

        account = Account(**account_data)
        test_db.add(account)
        test_db.commit()
        test_db.refresh(account)

        assert account.id is not None
        assert account.platform_id == sample_platform.id
        assert account.email == account_data["email"]
        assert account.password == account_data["password"]
        assert account.memo == account_data["memo"]
        assert isinstance(account.created_at, datetime)
        assert account.updated_at is None

    def test_create_account_without_memo(self, test_db, sample_platform):
        """메모 없이 계정 생성 테스트"""
        account = Account(
            platform_id=sample_platform.id,
            email="platform@example.com",
            password="platformpass123"
        )
        test_db.add(account)
        test_db.commit()

        assert account.id is not None
        assert account.memo is None

    def test_create_account_duplicate_email(self, test_db, sample_platform):
        """중복된 이메일로 계정 생성 시도 테스트"""
        account1 = Account(
            platform_id=sample_platform.id,
            email="duplicate@example.com",
            password="pass123"
        )
        test_db.add(account1)
        test_db.commit()

        with pytest.raises(IntegrityError):
            account2 = Account(
                platform_id=sample_platform.id,
                email="duplicate@example.com",
                password="pass456"
            )
            test_db.add(account2)
            test_db.commit()

    def test_read_account(self, test_db, sample_platform):
        """계정 정보 조회 테스트"""
        account = Account(
            platform_id=sample_platform.id,
            email="read@example.com",
            password="readpass123"
        )
        test_db.add(account)
        test_db.commit()

        retrieved_account = test_db.query(Account).filter(
            Account.email == "read@example.com"
        ).first()

        assert retrieved_account is not None
        assert retrieved_account.platform_id == sample_platform.id
        assert retrieved_account.email == "read@example.com"

    def test_update_account_info(self, test_db, sample_platform):
        """계정 정보 수정 테스트"""
        account = Account(
            platform_id=sample_platform.id,
            email="old@example.com",
            password="oldpass"
        )
        test_db.add(account)
        test_db.commit()

        account.email = "new@example.com"
        account.password = "newpass"
        account.memo = "수정된 메모"
        test_db.commit()
        test_db.refresh(account)

        assert account.email == "new@example.com"
        assert account.password == "newpass"
        assert account.memo == "수정된 메모"
        assert account.updated_at is not None

    def test_delete_account(self, test_db, sample_platform):
        """계정 삭제 테스트"""
        account = Account(
            platform_id=sample_platform.id,
            email="delete@example.com",
            password="deletepass"
        )
        test_db.add(account)
        test_db.commit()

        test_db.delete(account)
        test_db.commit()

        deleted_account = test_db.query(Account).filter(
            Account.email == "delete@example.com"
        ).first()
        assert deleted_account is None

    def test_create_multiple_accounts_for_platform(self, test_db, sample_platform):
        """한 플랫폼에 여러 계정 생성 테스트"""
        accounts = [
            Account(
                platform_id=sample_platform.id,
                email=f"account{i}@example.com",
                password=f"pass{i}"
            ) for i in range(1, 4)
        ]

        test_db.add_all(accounts)
        test_db.commit()

        platform_accounts = test_db.query(Account).filter(
            Account.platform_id == sample_platform.id
        ).all()
        assert len(platform_accounts) == 3

    def test_account_platform_relationship(self, test_db):
        """플랫폼 연결 검증 테스트"""
        with pytest.raises(IntegrityError):
            account = Account(
                platform_id=999,  # 존재하지 않는 플랫폼 ID
                email="invalid@example.com",
                password="pass123"
            )
            test_db.add(account)
            test_db.commit()

    def test_account_required_fields(self, test_db, sample_platform):
        """필수 필드 검증 테스트"""
        required_fields = [
            {"email": "test@example.com", "password": "pass123"},  # platform_id 누락
            {"platform_id": sample_platform.id, "password": "pass123"},  # email 누락
            {"platform_id": sample_platform.id, "email": "test@example.com"}  # password 누락
        ]

        for fields in required_fields:
            with pytest.raises(IntegrityError):
                account = Account(**fields)
                test_db.add(account)
                test_db.commit()
            test_db.rollback()

    def test_account_availability_management(self, test_db, sample_platform):
        """계정 사용 가능 상태 관리 테스트"""
        account = Account(
            platform_id=sample_platform.id,
            email="available@example.com",
            password="pass123",
            is_available=True
        )
        test_db.add(account)
        test_db.commit()

        account.is_available = False
        test_db.commit()
        test_db.refresh(account)

        assert account.is_available == False 