import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.core.auth import get_password_hash

# 테스트용 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# 테스트용 데이터베이스 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # 테스트 데이터베이스 생성
    Base.metadata.create_all(bind=engine)
    
    # 테스트 사용자 생성
    db = TestingSessionLocal()
    admin_user = User(
        email="admin@wrsoft.co.kr",
        full_name="관리자",
        hashed_password=get_password_hash("admin1234"),
        is_active=True,
        is_approved=True,
        is_superuser=True
    )
    db.add(admin_user)
    db.commit()
    
    yield
    
    # 테스트 후 정리
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
