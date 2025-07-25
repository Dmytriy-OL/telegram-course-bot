from sqlalchemy.future import select
from app.database.core.models import SessionLocal, User


async def user_exists(username: str, email: str) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where((User.username == username) | (User.email == email))
        )
        return result.scalar_one_or_none() is not None


async def save_user(username: str, email: str, password_hash: str) -> None:
    async with SessionLocal() as session:
        new_user = User(username=username, email=email, password_hash=password_hash)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
