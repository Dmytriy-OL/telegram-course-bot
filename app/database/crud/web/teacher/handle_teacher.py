from sqlalchemy.future import select

from app.database.core.base import SessionLocal
from app.database.core.models import Teacher, User
from app.database.crud.web.repository.user_repo import update_user_data


# async def create_teacher(
#         name: str,
#         surname: str,
#         sex: GenderSelection,
#         english_level: EnglishLevel,
#         experience_years: int = 0,
#         students_count: int = 0,
#         roles: list | None = None,
#         description: str | None = None,
#         phone_number: str | None = None,
#         show_phone: bool | False = False,
#         social_links: dict | None = None,
#         photo: str | None = None
# ) -> bool:
#     async with SessionLocal() as session:
#         teacher = Teacher(
#             name=name,
#             surname=surname,
#             sex=sex,
#             students_count=students_count,
#             experience_years=experience_years,
#             roles=roles,
#             english_level=english_level,
#             description=description,
#             phone_number=phone_number,
#             show_phone=show_phone,
#             social_links=social_links,
#             photo=photo
#         )
#         session.add(teacher)
#         await session.commit()
#         return True


async def all_teacher():
    async with SessionLocal() as session:
        result = await session.execute(select(Teacher))
        administrators = result.scalars().all()
        return administrators


# async def create_teacher_request(user: User, data: dict):
#     async with SessionLocal() as session:
#         db_user = await session.get(User, user.id)
#
#         if not db_user:
#             raise TeacherApplicationError("Користувача не знайдено")
#
#         if db_user.is_teacher:
#             raise TeacherApplicationError("Ви вже маєте статус викладача")
#
#         db_user.name = data["name"]
#         db_user.surname = data["surname"]
#         db_user.is_teacher = True
#
#         teacher = Teacher(
#             user_id=db_user.id,
#             language=[data["language"]],
#             experience=data["experience"],
#             english_level=data["english_level"],
#             phone_number=data["phone"],
#             description=data["bio"],
#             social_links=data["social_networks"],
#             price=data["price"]
#         )
#
#         session.add(teacher)
#         await session.commit()

