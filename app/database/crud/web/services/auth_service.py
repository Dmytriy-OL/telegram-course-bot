from werkzeug.security import check_password_hash
from typing import Literal
from app.database.crud.web.repository.user_repo import get_user_by_email
from app.database.core.models import User

AuthStatus = Literal["ok", "not_found", "wrong_password"]


async def authenticate_user(email: str, password: str) -> tuple[AuthStatus, User | None]:
    user = await get_user_by_email(email)

    if not user:
        return "not_found", None
    if not check_password_hash(user.password_hash, password):
        return "wrong_password", None
    return "ok", user
