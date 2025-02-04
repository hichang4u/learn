from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.platform import Platform
from app.models.account import Account
from app.models.user import User

def init_db():
    # 데이터베이스 테이블 생성
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 초기 플랫폼 데이터 추가
        platforms = [
            Platform(
                id=1,
                name='인프런',
                url='https://www.inflearn.com',
                logo='https://cdn.inflearn.com/assets/brand/logo.png',
                description='인프런은 개발자를 위한 온라인 강의 플랫폼입니다.',
                created_at=datetime.now()
            ),
            Platform(
                id=2,
                name='유데미',
                url='https://www.udemy.com',
                logo='https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg',
                description='유데미는 다양한 분야의 온라인 강의를 제공하는 글로벌 플랫폼입니다.',
                created_at=datetime.now()
            )
        ]
        
        # 데이터베이스에 플랫폼 추가
        for platform in platforms:
            db.add(platform)
        db.commit()

        # 초기 계정 데이터 추가
        accounts = []
        
        # 인프런 계정 10개 생성
        for i in range(1, 11):
            accounts.append(Account(
                platform_id=1,
                email=f'inflearn{i}',
                hashed_password=get_password_hash(f'inflearn{i}'),
                memo=f'인프런 테스트 계정 {i}번',
                is_active=True,
                created_at=datetime.now()
            ))

        # 유데미 계정 10개 생성
        for i in range(1, 11):
            accounts.append(Account(
                platform_id=2,
                email=f'udemy{i}',
                hashed_password=get_password_hash(f'udemy{i}'),
                memo=f'유데미 테스트 계정 {i}번',
                is_active=True,
                created_at=datetime.now()
            ))
        
        # 데이터베이스에 계정 추가
        for account in accounts:
            db.add(account)
        
        # 관리자 계정 추가
        admin_user = User(
            email="admin@wrsoft.co.kr",
            hashed_password=get_password_hash("admin1234"),
            is_active=True,
            is_approved=True,
            is_superuser=True,
            full_name="관리자",
            created_at=datetime.now()
        )
        db.add(admin_user)
        
        # 일반 사용자 계정 추가
        test_user = User(
            email="test@wrsoft.co.kr",
            hashed_password=get_password_hash("test1234"),
            is_active=True,
            is_approved=True,
            is_superuser=False,
            full_name="테스트 사용자",
            created_at=datetime.now()
        )
        db.add(test_user)
        
        # 변경사항 저장
        db.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 