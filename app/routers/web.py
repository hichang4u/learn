import sys
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.dependencies import get_current_user_or_none, login_required, get_db
from app.models import User
from app import crud
from app.crud import user as user_crud
from app import schemas
from app.core.security import get_password_hash, verify_password, create_access_token

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "이메일 또는 비밀번호가 올바르지 않습니다."}
        )
    
    if not user.is_approved:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "관리자 승인 대기 중입니다. 승인 후 로그인이 가능합니다."}
        )
    
    # 로그인 성공
    access_token = create_access_token(user.id)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        max_age=1800,
        secure=False  # 개발 환경에서는 False
    )
    return response

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(
    request: Request,
    user: Annotated[User | None, Depends(get_current_user_or_none)]
):
    """회원가입 페이지"""
    # 이미 로그인한 경우 메인 페이지로 리다이렉트
    if user:
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse(
        "auth/signup.html",
        {"request": request}
    )

@router.post("/signup")
async def signup_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    full_name: str = Form(...),
    position: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"회원가입 시도 - 이메일: {username}, 이름: {full_name}, 직급: {position}")
        
        # 1. 기본 유효성 검사
        if not username or not password or not full_name or not position:
            raise ValueError("모든 필드를 입력해주세요.")
        
        if password != confirm_password:
            logger.warning(f"비밀번호 불일치 - 이메일: {username}")
            return templates.TemplateResponse(
                "auth/signup.html",
                {"request": request, "error": "비밀번호가 일치하지 않습니다."}
            )
        
        # 2. Position Enum 검증
        try:
            from app.models.user import Position
            logger.info(f"직급 검증 시도 - 입력값: {position}")
            position_enum = Position(position)
            logger.info(f"직급 검증 성공 - 변환값: {position_enum}")
        except ValueError:
            logger.error(f"잘못된 직급 입력 - 입력값: {position}")
            return templates.TemplateResponse(
                "auth/signup.html",
                {"request": request, "error": f"올바르지 않은 직급입니다. 가능한 직급: {', '.join([p.value for p in Position])}"}
            )
        
        # 3. 사용자 생성
        try:
            user_in = schemas.UserCreate(
                email=username,
                full_name=full_name,
                position=position_enum,
                password=password
            )
            logger.info("UserCreate 스키마 생성 완료")
            
            user = user_crud.create(db, obj_in=user_in)
            logger.info(f"사용자 생성 완료 - ID: {user.id}")
            
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "message": "회원가입이 완료되었습니다. 관리자 승인 후 로그인이 가능합니다."
                }
            )
            
        except ValueError as e:
            logger.error(f"사용자 생성 실패 - {str(e)}")
            return templates.TemplateResponse(
                "auth/signup.html",
                {"request": request, "error": str(e)}
            )
            
        except Exception as e:
            logger.error(f"사용자 생성 중 예외 발생 - {str(e)}", exc_info=True)
            db.rollback()
            return templates.TemplateResponse(
                "auth/signup.html",
                {"request": request, "error": "회원가입 처리 중 오류가 발생했습니다. 다시 시도해 주세요."}
            )
            
    except Exception as e:
        logger.error(f"회원가입 처리 중 예외 발생 - {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "회원가입 처리 중 오류가 발생했습니다. 다시 시도해 주세요."}
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

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    current_user: User = Depends(get_current_user_or_none),
    db: Session = Depends(get_db)
):
    if not current_user or not current_user.is_superuser:
        return RedirectResponse(url="/login", status_code=303)
    
    # 승인 대기 중인 사용자
    pending_users = db.query(User).filter(
        User.is_approved == False
    ).order_by(User.created_at.desc()).all()
    
    # 승인된 사용자
    approved_users = db.query(User).filter(
        User.is_approved == True
    ).order_by(User.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "current_user": current_user,
            "pending_users": pending_users,
            "approved_users": approved_users
        }
    )

@router.post("/admin/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_or_none),
    db: Session = Depends(get_db)
):
    if not current_user or not current_user.is_superuser:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_approved = True
        user.is_active = True
        db.commit()
    
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/admin/users/{user_id}/reject")
async def reject_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_or_none),
    db: Session = Depends(get_db)
):
    if not current_user or not current_user.is_superuser:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/admin/users/{user_id}/toggle")
async def toggle_user_status(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_or_none),
    db: Session = Depends(get_db)
):
    if not current_user or not current_user.is_superuser:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(User).filter(User.id == user_id).first()
    if user and not user.is_superuser:
        user.is_active = not user.is_active
        db.commit()
    
    return RedirectResponse(url="/admin/users", status_code=303)

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

@router.get("/error")
async def error_page(
    request: Request,
    error_code: str = "500",
    error_title: str = "오류 발생",
    error_message: str = "알 수 없는 오류가 발생했습니다.",
    show_login: bool = False
):
    """오류 페이지를 표시합니다."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_code": error_code,
            "error_title": error_title,
            "error_message": error_message,
            "show_login": show_login
        }
    ) 