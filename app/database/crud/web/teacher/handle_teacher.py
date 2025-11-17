from sqlalchemy.future import select

from app.database.core.models import Teacher, GenderSelection, EnglishLevel
from app.database.core.models import SessionLocal


async def create_teacher(
        name: str,
        surname: str,
        sex: GenderSelection,
        english_level: EnglishLevel,
        experience_years: int = 0,
        students_count: int = 0,
        roles: list | None = None,
        description: str | None = None,
        phone_number: str | None = None,
        show_phone: bool | False = False,
        social_links: dict | None = None,
        photo: str | None = None
) -> bool:
    async with SessionLocal() as session:
        teacher = Teacher(
            name=name,
            surname=surname,
            sex=sex,
            students_count=students_count,
            experience_years=experience_years,
            roles=roles,
            english_level=english_level,
            description=description,
            phone_number=phone_number,
            show_phone=show_phone,
            social_links=social_links,
            photo=photo
        )
        session.add(teacher)
        await session.commit()
        return True


async def all_teacher():
    async with SessionLocal() as session:
        result = await session.execute(select(Teacher))
        administrators = result.scalars().all()
        return administrators
