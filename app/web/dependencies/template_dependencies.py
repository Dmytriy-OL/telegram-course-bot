from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core.models import User
from app.web.dependencies.db import get_db


def get_session_user(request: Request):
    return request.session.get("user")


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_data = request.session.get("user")
    if not user_data:
        return None

    return await db.get(User, user_data["id"])