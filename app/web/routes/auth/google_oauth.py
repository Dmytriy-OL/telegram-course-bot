import os
import logging
from fastapi.responses import RedirectResponse
from fastapi import Request, APIRouter

from authlib.integrations.starlette_client import OAuth
from app.database.crud.web.repository.user_repo import save_user, confirm_email, \
    get_user_by_email, update_user_google_id

from app.web.utils.tokens import verify_token
from app.web.templates import templates

oauth = OAuth()
router = APIRouter()
logger = logging.getLogger(__name__)


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
        user = await get_user_by_email(email)
        if not user:
            await save_user(email=email, password_hash=None, google_id=google_id, name=name, surname=surname)
        else:
            if not user.google_id:
                await update_user_google_id(user, google_id)

        request.session["user"] = {
            "email": email,
            "name": name,
            "surname": surname
        }
        return RedirectResponse(url="/")
    except Exception as e:
        logger.error(f"🔴 Помилка при Google авторизації: {e}")
        return RedirectResponse(url="/login?error=google_oauth_failed")


oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
