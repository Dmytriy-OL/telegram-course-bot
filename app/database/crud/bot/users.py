from sqlalchemy.future import select
from app.database.core.models import User
from app.database.core.base import SessionLocal


async def set_user(tg_id: int, login: str, name: str = None, surname: str = None) -> User:
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            user = User(tg_id=tg_id, name=name, surname=surname, login=login)
            session.add(user)
        else:
            if name is None or surname is None:
                user.login = login
            else:
                user.name = name
                user.surname = surname
                user.login = login

        await session.commit()
        await session.refresh(user)
        return user
