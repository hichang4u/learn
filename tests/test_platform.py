import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Platform
from datetime import datetime

class TestPlatform:
    """플랫폼 모델 테스트 클래스"""

    def test_create_platform_success(self, test_db):
        """플랫폼 생성 성공 테스트"""
        # Given
        platform_data = {
            "name": "인프런",
            "url": "https://www.inflearn.com",
            "logo": "https://www.inflearn.com/logo.png",
            "description": "국내 최대 온라인 강의 플랫폼"
        }

        # When
        platform = Platform(**platform_data)
        test_db.add(platform)
        test_db.commit()
        test_db.refresh(platform)

        # Then
        assert platform.id is not None
        assert platform.name == platform_data["name"]
        assert platform.url == platform_data["url"]
        assert platform.logo == platform_data["logo"]
        assert platform.description == platform_data["description"]
        assert isinstance(platform.created_at, datetime)
        assert platform.updated_at is None

    def test_create_platform_without_optional_fields(self, test_db):
        """선택적 필드 없이 플랫폼 생성 테스트"""
        # Given
        platform_data = {
            "name": "유데미",
            "url": "https://www.udemy.com"
        }

        # When
        platform = Platform(**platform_data)
        test_db.add(platform)
        test_db.commit()

        # Then
        assert platform.id is not None
        assert platform.name == platform_data["name"]
        assert platform.url == platform_data["url"]
        assert platform.logo is None
        assert platform.description is None

    def test_create_platform_duplicate_name(self, test_db):
        """중복된 플랫폼 이름 생성 시도 테스트"""
        # Given
        platform1 = Platform(name="테스트플랫폼", url="https://test1.com")
        test_db.add(platform1)
        test_db.commit()

        # When & Then
        platform2 = Platform(name="테스트플랫폼", url="https://test2.com")
        test_db.add(platform2)
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_read_platform(self, test_db):
        """플랫폼 조회 테스트"""
        # Given
        platform = Platform(
            name="코세라",
            url="https://www.coursera.org",
            description="글로벌 교육 플랫폼"
        )
        test_db.add(platform)
        test_db.commit()

        # When
        retrieved_platform = test_db.query(Platform).filter(
            Platform.name == "코세라"
        ).first()

        # Then
        assert retrieved_platform is not None
        assert retrieved_platform.name == "코세라"
        assert retrieved_platform.url == "https://www.coursera.org"
        assert retrieved_platform.description == "글로벌 교육 플랫폼"

    def test_update_platform(self, test_db):
        """플랫폼 정보 수정 테스트"""
        # Given
        platform = Platform(name="패스트캠퍼스", url="https://fastcampus.co.kr")
        test_db.add(platform)
        test_db.commit()

        # When
        platform.description = "실무 중심 교육"
        platform.logo = "https://fastcampus.co.kr/logo.png"
        test_db.commit()
        test_db.refresh(platform)

        # Then
        assert platform.description == "실무 중심 교육"
        assert platform.logo == "https://fastcampus.co.kr/logo.png"
        assert platform.updated_at is not None

    def test_delete_platform(self, test_db):
        """플랫폼 삭제 테스트"""
        # Given
        platform = Platform(name="러닝스푼", url="https://learningspoons.com")
        test_db.add(platform)
        test_db.commit()

        # When
        test_db.delete(platform)
        test_db.commit()

        # Then
        deleted_platform = test_db.query(Platform).filter(
            Platform.name == "러닝스푼"
        ).first()
        assert deleted_platform is None

    def test_create_platform_missing_required_fields(self, test_db):
        """필수 필드 누락 시 플랫폼 생성 테스트"""
        # Given & When & Then
        with pytest.raises(IntegrityError):
            platform = Platform(url="https://example.com")  # name 필드 누락
            test_db.add(platform)
            test_db.commit()

    def test_bulk_create_platforms(self, test_db):
        """다수의 플랫폼 일괄 생성 테스트"""
        # Given
        platforms = [
            Platform(name="플랫폼1", url="https://platform1.com"),
            Platform(name="플랫폼2", url="https://platform2.com"),
            Platform(name="플랫폼3", url="https://platform3.com")
        ]

        # When
        test_db.add_all(platforms)
        test_db.commit()

        # Then
        count = test_db.query(Platform).count()
        assert count == 3

    def test_query_platforms_order_by_name(self, test_db):
        """플랫폼 이름순 정렬 조회 테스트"""
        # Given
        platforms = [
            Platform(name="C플랫폼", url="https://c.com"),
            Platform(name="A플랫폼", url="https://a.com"),
            Platform(name="B플랫폼", url="https://b.com")
        ]
        test_db.add_all(platforms)
        test_db.commit()

        # When
        ordered_platforms = test_db.query(Platform).order_by(Platform.name).all()

        # Then
        assert len(ordered_platforms) == 3
        assert ordered_platforms[0].name == "A플랫폼"
        assert ordered_platforms[1].name == "B플랫폼"
        assert ordered_platforms[2].name == "C플랫폼"
