from typing import Annotated

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_current_user_or_none, login_required
from app.models import User

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: Annotated[User, Depends(login_required)]
):
    """메인 페이지"""
    return templates.TemplateResponse(
        "pages/calendar.html",
        {"request": request, "user": user}
    )

@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page(
    request: Request,
    user: Annotated[User, Depends(login_required)]
):
    """사용 일정 페이지"""
    return templates.TemplateResponse(
        "pages/calendar.html",
        {"request": request, "user": user}
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: Annotated[User | None, Depends(get_current_user_or_none)]
):
    """로그인 페이지"""
    # 이미 로그인한 경우 메인 페이지로 리다이렉트
    if user:
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )

@router.get("/platforms", response_class=HTMLResponse)
async def platforms_page(
    request: Request,
    user: Annotated[User, Depends(login_required)]
):
    """플랫폼 관리 페이지"""
    return templates.TemplateResponse(
        "admin/platforms.html",
        {"request": request, "user": user}
    )

@router.get("/accounts", response_class=HTMLResponse)
async def accounts_page(
    request: Request,
    current_user: Annotated[User, Depends(login_required)]
):
    """계정 관리 페이지"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")
    return templates.TemplateResponse(
        "admin/accounts.html",
        {"request": request}
    )

@router.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request,
    user: Annotated[User, Depends(login_required)]
):
    """사용자 관리 페이지"""
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "user": user}
    )

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    user: Annotated[User, Depends(login_required)]
):
    """설정 페이지"""
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "user": user}
    )

@router.get("/reservations", response_class=HTMLResponse)
async def admin_reservations_page(
    request: Request,
    user: Annotated[User, Depends(login_required)]
):
    """신청 관리 페이지"""
    if request.session.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근할 수 있습니다."
        )
    return templates.TemplateResponse(
        "admin/reservations.html",
        {"request": request, "user": user}
    )

@router.get("/request", response_class=HTMLResponse)
async def request_page(
    request: Request,
    user: Annotated[User, Depends(login_required)]
):
    """계정 신청 페이지"""
    return templates.TemplateResponse(
        "pages/request.html",
        {"request": request, "user": user}
    )

@router.get("/my-reservations", response_class=HTMLResponse)
async def my_reservations_page(
    request: Request,
    user: Annotated[User, Depends(login_required)]
):
    """내 신청 현황 페이지"""
    return templates.TemplateResponse(
        "pages/my_reservations.html",
        {"request": request, "user": user}
    ) 