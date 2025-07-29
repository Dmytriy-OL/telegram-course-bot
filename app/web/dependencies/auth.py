import os

from fastapi import Request, HTTPException, status, Form
from authlib.integrations.starlette_client import OAuth
from starlette.responses import HTMLResponse

from app.database.crud.web.registration import get_user_by_email, user_exists, authenticate_user
from app.database.core.models import User
from app.web.templates import templates

oauth = OAuth()


async def get_current_user(request: Request) -> User:
    email = request.session.get("user")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def validate_login_form(request: Request, email: str = Form(...),
                              password: str = Form(...)) -> User | HTMLResponse:
    auth_status, user = await authenticate_user(email, password)
    match auth_status:
        case "not_found":
            return templates.TemplateResponse("login.html", {"request": request, "error": "Користувача не знайдено",
                                                             "email": email},
                                              status_code=400)
        case "wrong_password":
            return templates.TemplateResponse("login.html", {"request": request, "error": "Невірний пароль",
                                                             "email": email},
                                              status_code=400)
        case "ok":
            return user


async def validate_register_form(password: str, password_confirm: str, email: str):
    if password != password_confirm:
        return "Паролі не співпадають!"
    if await user_exists(email):
        return "Такий логін вже існує!"
    return None


oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
