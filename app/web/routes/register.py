import logging
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from datetime import date
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_303_SEE_OTHER
from app.web.dependencies.auth_dependencies import oauth, validate_register_form, user_exists, parse_register_form
from werkzeug.security import generate_password_hash
from app.database.crud.web.repository.user_repo import validate_user_unique, save_user, confirm_email, \
    pending_user
from app.web.schemas.forms import RegisterForm
from app.web.templates import templates
from app.web.utils.tokens import generate_token
from app.web.utils.email_sender import send_verification_email
from app.web.utils.tokens import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "form_values": {}})


@router.post("/register", response_class=HTMLResponse)
async def register_post(
        request: Request,
        form_data: RegisterForm = Depends(parse_register_form),
):
    form_values = form_data.model_dump()

    try:
        await validate_user_unique(form_data.email, form_data.username)
    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": str(e),
                "form_values": form_values
            }
        )

    birth_date = form_data.birth_date
    password_hash = generate_password_hash(form_data.password)

    try:
        await pending_user(email=form_data.email, username=form_data.username, password_hash=password_hash,
                           birth_date=birth_date)
    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": str(e),
                "form_values": form_values
            }
        )

    # підтвердження ектроной адреси
    # token = generate_token(form_data.email)
    # send_verification_email(form_data.email, token)
    # return templates.TemplateResponse("register.html", {
    #     "request": request,
    #     "form_values": form_data.model_dump(),
    #     "email_sent": True,
    #     "email": form_data.email
    # })

    # без підтвердження
    await confirm_email(form_data.email)
    request.session["user"] = form_data.email
    return RedirectResponse(url="/", status_code=303)




@router.get("/verify-email")
async def verify_email(request: Request, token: str):
    try:
        email = verify_token(token)
    except Exception:
        return templates.TemplateResponse("verify_result.html", {
            "request": request,
            "success": False,
            "message": "Недійсний або прострочений токен"
        })
    try:
        await confirm_email(email)
    except ValueError as e:
        return templates.TemplateResponse("verify_result.html", {
            "request": request,
            "success": False,
            "message": str(e)
        })

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


