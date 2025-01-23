import pytest
from sqlalchemy.exc import IntegrityError
from app.models import User, UserRole
from datetime import datetime

class TestUser:
    """사용자 모델 테스트 클래스"""

    def test_create_user_success(self, test_db):
        """사용자 생성 성공 테스트"""
        # Given
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "hashedpassword123",
            "role": UserRole.USER
        }

        # When
        user = User(**user_data)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Then
        assert user.id is not None
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.password == user_data["password"]
        assert user.role == UserRole.USER
        assert isinstance(user.created_at, datetime)
        assert user.updated_at is None

    def test_create_admin_user(self, test_db):
        """관리자 사용자 생성 테스트"""
        # Given
        admin_data = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "adminpass123",
            "role": UserRole.ADMIN
        }

        # When
        admin = User(**admin_data)
        test_db.add(admin)
        test_db.commit()

        # Then
        assert admin.role == UserRole.ADMIN

    def test_create_user_duplicate_username(self, test_db):
        """중복된 사용자명 생성 시도 테스트"""
        # Given
        user1 = User(
            username="testuser",
            email="test1@example.com",
            password="pass123"
        )
        test_db.add(user1)
        test_db.commit()

        # When & Then
        with pytest.raises(IntegrityError):
            user2 = User(
                username="testuser",  # 중복된 username
                email="test2@example.com",
                password="pass456"
            )
            test_db.add(user2)
            test_db.commit()

    def test_create_user_duplicate_email(self, test_db):
        """중복된 이메일 생성 시도 테스트"""
        # Given
        user1 = User(
            username="user1",
            email="test@example.com",
            password="pass123"
        )
        test_db.add(user1)
        test_db.commit()

        # When & Then
        with pytest.raises(IntegrityError):
            user2 = User(
                username="user2",
                email="test@example.com",  # 중복된 email
                password="pass456"
            )
            test_db.add(user2)
            test_db.commit()

    def test_update_user_profile(self, test_db):
        """사용자 프로필 수정 테스트"""
        # Given
        user = User(
            username="oldname",
            email="old@example.com",
            password="oldpass"
        )
        test_db.add(user)
        test_db.commit()

        # When
        user.username = "newname"
        user.email = "new@example.com"
        test_db.commit()
        test_db.refresh(user)

        # Then
        assert user.username == "newname"
        assert user.email == "new@example.com"
        assert user.updated_at is not None

    def test_create_user_missing_required_fields(self, test_db):
        """필수 필드 누락 시 사용자 생성 테스트"""
        required_fields = [
            {"email": "test@example.com", "password": "pass123"},  # username 누락
            {"username": "testuser", "password": "pass123"},  # email 누락
            {"username": "testuser", "email": "test@example.com"}  # password 누락
        ]

        for fields in required_fields:
            with pytest.raises(IntegrityError):
                user = User(**fields)
                test_db.add(user)
                test_db.commit()
            test_db.rollback()

    def test_default_user_role(self, test_db):
        """기본 사용자 역할 테스트"""
        # Given
        user = User(
            username="testuser",
            email="test@example.com",
            password="pass123"
        )

        # When
        test_db.add(user)
        test_db.commit()

        # Then
        assert user.role == UserRole.USER

    def test_query_users_by_role(self, test_db):
        """역할별 사용자 조회 테스트"""
        # Given
        users = [
            User(username="user1", email="user1@example.com", password="pass1", role=UserRole.USER),
            User(username="admin1", email="admin1@example.com", password="pass2", role=UserRole.ADMIN),
            User(username="user2", email="user2@example.com", password="pass3", role=UserRole.USER),
            User(username="admin2", email="admin2@example.com", password="pass4", role=UserRole.ADMIN)
        ]
        test_db.add_all(users)
        test_db.commit()

        # When
        admin_users = test_db.query(User).filter(User.role == UserRole.ADMIN).all()
        normal_users = test_db.query(User).filter(User.role == UserRole.USER).all()

        # Then
        assert len(admin_users) == 2
        assert len(normal_users) == 2
        assert all(user.role == UserRole.ADMIN for user in admin_users)
        assert all(user.role == UserRole.USER for user in normal_users) 