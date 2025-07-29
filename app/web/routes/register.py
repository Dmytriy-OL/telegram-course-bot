import logging
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse

from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_303_SEE_OTHER
from app.web.dependencies.auth_dependencies import oauth, validate_register_form, validate_login_form
from werkzeug.security import generate_password_hash
from app.database.crud.web.repository.user_repo import user_exists, save_user
from app.web.schemas.forms import RegisterForm
from app.database.core.models import User
from app.web.templates import templates

from pydantic import ValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, user_or_response: User | HTMLResponse = Depends(validate_login_form)):
    if isinstance(user_or_response, HTMLResponse):
        return user_or_response

    request.session["user"] = user_or_response.email
    return RedirectResponse(url="/", status_code=303)


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_post(request: Request):
    form = await request.form()
    try:
        form_data = RegisterForm(
            email=form.get("email"),
            password=form.get("password"),
            password_confirm=form.get("password_confirm")
        )
    except ValidationError as e:
        raw_msg = e.errors()[0].get('msg', 'Помилка валідації')
        error_message = raw_msg.replace("Value error, ", "")
        return templates.TemplateResponse("register.html", {"request": request, "error": error_message})

    if await user_exists(form_data.email):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Такий логін вже існує!"})

    password_hash = generate_password_hash(form_data.password)
    await save_user(email=form_data.email, password_hash=password_hash)
    request.session["user"] = form_data.email
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
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info:
            return RedirectResponse(url="/register")

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

    except Exception as e:
        logger.error(f"🔴 Помилка при Google авторизації: {e}")
        return RedirectResponse(url="/login?error=google_oauth_failed")
