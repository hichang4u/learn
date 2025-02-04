from fastapi.testclient import TestClient
import pytest
from jose import jwt
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_login_and_token_validation():
    """로그인 및 토큰 검증 테스트"""
    # 1. 로그인 테스트
    login_data = {
        "username": "admin@wrsoft.co.kr",
        "password": "admin1234",
        "grant_type": "password"
    }
    
    response = client.post("/api/auth/login", data=login_data)
    print("로그인 응답:", response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    token = response.json()["access_token"]
    
    # 2. 토큰 디코딩 테스트
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        print("토큰 페이로드:", payload)
        assert "sub" in payload
        assert payload["sub"] == login_data["username"]
    except Exception as e:
        pytest.fail(f"토큰 디코딩 실패: {str(e)}")
    
    # 3. /me 엔드포인트 테스트
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/auth/me", headers=headers)
    print("/me 응답:", me_response.json())
    assert me_response.status_code == 200
    assert me_response.json()["email"] == login_data["username"]

def test_invalid_token():
    """잘못된 토큰 테스트"""
    # 1. 토큰 없이 요청
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    
    # 2. 잘못된 형식의 토큰
    headers = {"Authorization": "Invalid Token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    
    # 3. Bearer 없는 토큰
    headers = {"Authorization": "some-token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    
    # 4. 만료된 토큰
    expired_token = jwt.encode(
        {"sub": "test@example.com", "exp": 1000000},  # 이미 만료된 시간
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401

def test_token_format():
    """토큰 형식 테스트"""
    login_data = {
        "username": "admin@wrsoft.co.kr",
        "password": "admin1234",
        "grant_type": "password"
    }
    
    # 1. 로그인 및 토큰 획득
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 2. 다양한 Authorization 헤더 형식 테스트
    test_cases = [
        (f"Bearer {token}", 200),  # 정상 케이스
        (f"bearer {token}", 401),  # 소문자 bearer
        (f"BEARER {token}", 401),  # 대문자 BEARER
        (f"Bearer  {token}", 401),  # 더블 스페이스
        (token, 401),  # Bearer 없음
        (f"Bearer{token}", 401),  # 스페이스 없음
        (f"Bearer {token} ", 401),  # 끝에 스페이스
    ]
    
    for auth_header, expected_status in test_cases:
        headers = {"Authorization": auth_header}
        response = client.get("/api/auth/me", headers=headers)
        print(f"테스트 케이스: {auth_header[:20]}... -> 상태 코드: {response.status_code}")
        assert response.status_code == expected_status 