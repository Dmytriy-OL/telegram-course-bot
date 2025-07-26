import os

from fastapi import Request, HTTPException, status
from authlib.integrations.starlette_client import OAuth

from app.database.crud.web.registration import get_user_by_email, user_exists
from app.database.core.models import User

oauth = OAuth()


async def get_current_user(request: Request) -> User:
    email = request.session.get("user")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def get_optional_user(request: Request) -> User | None:
    email = request.session.get("user")
    if not email:
        return None
    return await get_user_by_email(email)


async def require_guest(request: Request):
    if request.session.get("user"):
        raise HTTPException(status_code=400, detail="Ви вже авторизовані!")


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
