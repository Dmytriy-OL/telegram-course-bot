from sqlalchemy.future import select
from app.database.core.base import SessionLocal
from app.database.core.models import Teacher, User
from app.database.core.models.teacher import TeacherLanguage
from app.database.crud.web.teacher.exceptions import (
    UserAlreadyTeacherError,
    UserNotFoundError
)
from app.web.schemas.teacher import TeacherApplicationCreate


class TeacherRepository:
    async def create_teacher(self, user: User, data: TeacherApplicationCreate):
        async with SessionLocal() as session:

            # Оновлюємо користувача
            user.is_teacher = True
            user.name = data.name
            user.surname = data.surname
            session.add(user)

            # Створюємо Teacher без english_level та price
            teacher = Teacher(
                user_id=user.id,
                experience=data.experience,
                phone_number=data.phone,
                description=data.bio,
                social_links=data.social_networks,
            )
            session.add(teacher)
            await session.flush()  # щоб зʼявився teacher.id

            # Додаємо мови та ціни
            for lang in data.languages:
                session.add(
                    TeacherLanguage(
                        teacher_id=teacher.id,
                        language=lang.language,
                        level=lang.level,
                        price=lang.price
                    )
                )

            await session.commit()
            return teacher

