from sqlalchemy.future import select
from app.database.core.base import SessionLocal
from app.database.core.models import Teacher, User
from app.database.crud.web.teacher.exceptions import (
    UserAlreadyTeacherError,
    UserNotFoundError
)


class TeacherRepository:
    async def create_teacher(self, user_id: int, data):
        async with SessionLocal() as session:
            user = await session.get(User, user_id)

            if not user:
                raise UserNotFoundError("Користувача не знайдено")

            if user.is_teacher:
                raise UserAlreadyTeacherError("Ви вже маєте статус викладача")

            user.name = data.name
            user.surname = data.surname
            user.is_teacher = True

            teacher = Teacher(
                user_id=user.id,
                language=[data.language],
                experience=data.experience,
                english_level=data.english_level,
                phone_number=data.phone,
                description=data.bio,
                social_links=data.social_networks,
                price=data.price
            )

            session.add(teacher)
            await session.commit()
