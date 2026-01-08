from sqlalchemy.future import select
from app.database.core.base import SessionLocal
from app.database.core.models import Teacher, User
from app.database.core.models.teacher import TeacherLanguage
from app.database.crud.web.teacher.exceptions import (
    UserAlreadyTeacherError,
    UserNotFoundError
)
from app.web.schemas.teacher import ProfileUpdateData


class UserRepository:
    async def update_user(self, user: User, data: ProfileUpdateData):
        async with SessionLocal() as session:
            # Оновлюємо користувача
            user.name = data.first_name
            user.surname = data.last_name
            session.add(user)

            await session.commit()
