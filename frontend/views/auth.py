from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from werkzeug.security import generate_password_hash
from frontend.models.user import User
from frontend import db

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        "auth/signup.html",
        {"request": request}
    )

@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if password != confirm_password:
        # TODO: Add flash message functionality
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "비밀번호가 일치하지 않습니다"}
        )
    
    user = User.query.filter_by(username=username).first()
    if user:
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "이미 존재하는 아이디입니다"}
        )
    
    new_user = User(
        username=username,
        password=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()
    
    return RedirectResponse(url="/auth/login", status_code=303)
