from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr
    password: str
    remember_me: bool = False

class Token(BaseModel):
    """토큰 응답 스키마"""
    access_token: str
    token_type: str 