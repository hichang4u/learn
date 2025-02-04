from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import secrets
from typing import Optional

class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key
        self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in self.safe_methods:
            # 안전한 메소드는 CSRF 검증 생략
            response = await call_next(request)
            # GET 요청 시 새로운 CSRF 토큰 생성
            if request.method == "GET" and "csrf_token" not in request.session:
                csrf_token = self._generate_csrf_token()
                request.session["csrf_token"] = csrf_token
            return response

        # API 요청은 CSRF 검증 생략 (JWT 토큰으로 인증)
        if request.url.path.startswith("/api/"):
            return await call_next(request)

        # CSRF 토큰 검증
        csrf_token = request.headers.get("X-CSRF-Token")
        session_token = request.session.get("csrf_token")

        if not csrf_token or not session_token or csrf_token != session_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF 토큰이 유효하지 않습니다."
            )

        # 요청 처리
        response = await call_next(request)
        return response

    def _generate_csrf_token(self) -> str:
        """새로운 CSRF 토큰 생성"""
        return secrets.token_urlsafe(32) 