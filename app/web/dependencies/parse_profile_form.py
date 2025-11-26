from fastapi import Request, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from starlette.responses import HTMLResponse

from app.database.crud.web.repository.user_repo import get_user_by_email, user_exists
from app.database.crud.web.services.auth_service import authenticate_user
from app.database.core.models import User
from app.web.schemas.profile_form import ProfileUpdateForm
from app.web.templates import templates
from app.web.schemas.forms import RegisterForm
from pydantic import ValidationError, BaseModel
from datetime import datetime
from pydantic import ValidationError
from werkzeug.security import check_password_hash


class ChangePasswordForm(BaseModel):
    old_password: str
    new_password: str


async def parse_profile_form(
        name: str = Form(...),
        surname: str = Form(...),
        username: str = Form(None),
        birth_day: int = Form(...),
        birth_month: int = Form(...),
        birth_year: int = Form(...),

) -> ProfileUpdateForm:
    try:
        return ProfileUpdateForm(
            name=name,
            surname=surname,
            username=username,
            birth_day=birth_day,
            birth_month=birth_month,
            birth_year=birth_year
        )
    except ValidationError as e:
        raw = e.errors()[0].get("msg", "Помилка валідації")
        raise ValueError(raw)


async def parse_change_password_form(
        old_password: str = Form(...),
        new_password: str = Form(...),
) -> ChangePasswordForm:
    return ChangePasswordForm(
        old_password=old_password,
        new_password=new_password,
    )


async def check_password(password_hash: str | None, plain_password: str) -> bool:
    if not password_hash:
        return False
    return check_password_hash(password_hash, plain_password)

