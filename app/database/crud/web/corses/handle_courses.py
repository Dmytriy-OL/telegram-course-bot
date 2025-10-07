from sqlalchemy import update, delete, and_
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database.core.models import Courses, Administrator
from app.database.core.models import SessionLocal

from datetime import date


async def create_course(title: str, price: int, caption: str, lesson_count: int, teacher_id: int):
    async with SessionLocal() as session:
        add_course = Courses(title=title, price=price, caption=caption, lesson_count=lesson_count,
                             teacher_id=teacher_id)
        session.add(add_course)
        await session.commit()
        return True


async def all_courses():
    async with SessionLocal() as session:
        result = await session.execute(select(Courses).options(selectinload(Courses.teacher)))
        return result.scalars().all()

