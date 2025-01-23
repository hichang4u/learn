import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Platform
from datetime import datetime

# 테스트용 SQLite 메모리 DB 사용
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def test_db():
    """테스트용 데이터베이스 세션 픽스처"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # 외래 키 제약 조건 활성화
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')
    
    event.listen(engine, 'connect', _fk_pragma_on_connect)
    
    # 테스트용 DB 테이블 생성
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    
    try:
        yield db
    finally:
        db.close()
        # 테스트 후 DB 초기화
        Base.metadata.drop_all(bind=engine)
