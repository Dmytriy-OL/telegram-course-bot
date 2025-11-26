from fastapi import Request, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from starlette.responses import HTMLResponse

from app.database.crud.web.repository.user_repo import get_user_by_email, user_exists
from app.database.crud.web.services.auth_service import authenticate_user
from app.database.core.models import User
from app.web.templates import templates
from app.web.schemas.forms import RegisterForm
from pydantic import ValidationError


async def get_current_user(request: Request) -> User:
    session_user = request.session.get("user")

    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Not authenticated",
            headers={"Location": "/login"}
        )

    # підтримка dict і просто email
    email = session_user["email"] if isinstance(session_user, dict) else session_user

    if not email:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Empty email",
            headers={"Location": "/login"}
        )

    user = await get_user_by_email(email)

    if not user:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="User not found",
            headers={"Location": "/login"}
        )

    return user


async def validate_login_form(request: Request, email: str = Form(...),
                              password: str = Form(...)) -> User | HTMLResponse:
    auth_status, user = await authenticate_user(email, password)
    match auth_status:
        case "not_found":
            return templates.TemplateResponse("auth/login.html",
                                              {"request": request, "error": "Користувача не знайдено",
                                               "email": email},
                                              status_code=400)
        case "wrong_password":
            return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Невірний пароль",
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


async def get_authenticated_user(request: Request) -> User:
    session_user = request.session.get("user")

    if not session_user or not isinstance(session_user, dict):
        raise HTTPException(status_code=401, detail="Користувач не авторизований")

    email = session_user.get("email")

    user = await get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    return user


async def parse_register_form(
        # birth_day: int = Form(...),
        # birth_month: int = Form(...),
        # birth_year: int = Form(...),
        email: str = Form(...),
        # username: str = Form(..., alias="login"),
        password: str = Form(...),
        password_confirm: str = Form(...),
        terms: bool = Form(...)
):
    try:
        form_data = RegisterForm(
            # birth_day=birth_day,
            # birth_month=birth_month,
            # birth_year=birth_year,
            email=email,
            # username=username,
            password=password,
            password_confirm=password_confirm,
            terms=terms,
        )
    except ValidationError as e:
        raw_msg = e.errors()[0].get('msg', 'Помилка валідації')
        error_message = raw_msg.replace("Value error, ", "")
        return {"error": error_message}
    return form_data
