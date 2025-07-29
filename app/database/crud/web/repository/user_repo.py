from sqlalchemy.future import select
from app.database.core.models import User
from app.database.core.models import SessionLocal


async def get_user_by_email(email: str) -> User | None:
    async with SessionLocal() as session:
        return await session.scalar(select(User).where(User.email == email))


async def user_exists(email: str) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none() is not None


async def save_user(email: str, password_hash: str = None, google_id: str = None, name: str = None,
                    surname: str = None) -> None:
    async with SessionLocal() as session:
        new_user = User(email=email, password_hash=password_hash, google_id=google_id, name=name, surname=surname)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)