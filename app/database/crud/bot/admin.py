import asyncio
from sqlalchemy.future import select
from app.database.core.models import SessionLocal, Administrator


async def add_admin(tg_id: int, name: str, surname: str, login: str, main_admin: bool = False) -> None:
    async with SessionLocal() as session:
        new_admin = Administrator(tg_id=tg_id, name=name, surname=surname, login=login, main_admin=main_admin)
        session.add(new_admin)
        await session.commit()


async def get_role(tg_id: int) -> str:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Administrator).where(Administrator.tg_id == tg_id)
        )
        teacher = result.scalar_one_or_none()

        if teacher:
            return "admin" if teacher.main_admin == 1 else "teacher"

        return "user"


async def get_teacher_by_telegram_id(teacher_tg_id: int) -> Administrator | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Administrator).where(Administrator.tg_id == teacher_tg_id))
        return result.scalar_one_or_none()


if __name__ == '__main__':
    asyncio.run(add_admin(974638427, "Муровець", "Максим", "dimon20012", True))
