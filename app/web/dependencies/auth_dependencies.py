import os

from fastapi import Request, HTTPException, status, Form
from authlib.integrations.starlette_client import OAuth
from starlette.responses import HTMLResponse

from app.database.crud.web.repository.user_repo import get_user_by_email, user_exists
from app.database.crud.web.services.auth_service import authenticate_user
from app.database.core.models import User
from app.web.templates import templates
from app.web.schemas.forms import RegisterForm
from pydantic import ValidationError

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
    print("AUTH:", auth_status, user)
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


async def get_authenticated_user(request: Request) -> User | None:
    email = request.session.get("user")
    user = await get_user_by_email(email)
    return user


async def parse_register_form(
        birth_day: int = Form(...),
        birth_month: int = Form(...),
        birth_year: int = Form(...),
        email: str = Form(...),
        username: str = Form(..., alias="login"),
        password: str = Form(...),
        password_confirm: str = Form(...),
        terms: bool = Form(...)
):
    try:
        form_data = RegisterForm(
            birth_day=birth_day,
            birth_month=birth_month,
            birth_year=birth_year,
            email=email,
            username=username,
            password=password,
            password_confirm=password_confirm,
            terms=terms,
        )
    except ValidationError as e:
        raw_msg = e.errors()[0].get('msg', 'Помилка валідації')
        error_message = raw_msg.replace("Value error, ", "")
        raise ValueError(error_message)
    return form_data


oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
