from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_303_SEE_OTHER
from app.web.auth import oauth
from werkzeug.security import generate_password_hash
import os
from app.database.crud.web.registration import user_exists, save_user, authenticate_user

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    print(f"Пошта: {email}, Пароль: {password}")
    user = await authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Невірний email або пароль!"}
        )
    request.session["user"] = email
    return RedirectResponse(url="/", status_code=303)


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_post(
        request: Request,
        password: str = Form(...),
        password_confirm: str = Form(...),
        email: str = Form(...)
):
    if password != password_confirm:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Паролі не співпадають!"}
        )

    if await user_exists(email):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Такий логін вже існує!"}
        )

    password_hash = generate_password_hash(password)
    print(f"Пароль: {password}, Пошта: {email}")

    await save_user(email, password_hash)
    request.session["user"] = email
    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@router.get("/auth/google")
async def auth_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        return RedirectResponse(url="/register")  # fallback

    email = user_info["email"]
    google_id = user_info["sub"]
    name = user_info.get("given_name")
    surname = user_info.get("family_name")

    # Перевірка чи користувач вже існує
    user = await user_exists(email)
    if not user:
        await save_user(email=email, password_hash=None, google_id=google_id, name=name, surname=surname)

    request.session["user"] = email
    return RedirectResponse(url="/")
