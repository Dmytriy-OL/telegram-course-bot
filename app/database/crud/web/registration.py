from sqlalchemy.future import select
from app.database.core.models import SessionLocal, User
from werkzeug.security import check_password_hash


async def user_exists(email: str) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None


async def get_user_by_email(email: str) -> User | None:
    async with SessionLocal() as session:
        return await session.scalar(select(User).where(User.email == email))


async def save_user(email: str, password_hash: str = None, google_id: str = None, name: str = None,
                    surname: str = None) -> None:
    async with SessionLocal() as session:
        new_user = User(email=email, password_hash=password_hash, google_id=google_id, name=name, surname=surname)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)


async def authenticate_user(email: str, password: str) -> User | None:
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user: User | None = result.scalar_one_or_none()
        if not user:
            return None

        if not check_password_hash(user.password_hash, password):
            return None

        return user
