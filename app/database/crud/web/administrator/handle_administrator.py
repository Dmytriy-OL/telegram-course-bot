from sqlalchemy import update, delete, and_
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database.core.models import Administrator
from app.database.core.models import SessionLocal

from datetime import date


async def create_administrator(tg_id: int, name: str, surname: str, login: str, main_admin: bool):
    async with SessionLocal() as session:
        add_course = Administrator(tg_id=tg_id, name=name, surname=surname, login=login,
                                   main_admin=main_admin)
        session.add(add_course)
        await session.commit()
        return True


async def all_administrators():
    async with SessionLocal() as session:
        result = await session.execute(select(Administrator))
        administrators = result.scalars().all()
        return administrators
