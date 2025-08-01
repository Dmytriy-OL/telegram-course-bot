from sqlalchemy.future import select
from app.database.core.models import User
from app.database.core.models import SessionLocal
from datetime import date


async def get_user_by_email(email: str) -> User | None:
    async with SessionLocal() as session:
        return await session.scalar(select(User).where(User.email == email))


async def validate_user_unique(email: str, username: str) -> None:
    async with SessionLocal() as session:
        result_email = await session.execute(select(User).where(User.email == email))
        if result_email.scalar_one_or_none():
            raise ValueError("Така електронна адреса вже існує!")

        # Перевірка username
        result_username = await session.execute(select(User).where(User.username == username))
        if result_username.scalar_one_or_none():
            raise ValueError("Такий користувач вже існує!")


async def user_exists(email: str) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none() is not None


async def save_user(email: str, username: str = None, password_hash: str = None, google_id: str = None,
                    name: str = None,
                    surname: str = None, birth_date: date = None, terms_accepted: bool = False) -> None:
    async with SessionLocal() as session:
        new_user = User(email=email, username=username, password_hash=password_hash, google_id=google_id, name=name,
                        surname=surname, birth_date=birth_date, terms_accepted=terms_accepted)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
