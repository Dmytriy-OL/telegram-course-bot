from sqlalchemy.future import select
from app.database.core.models import SessionLocal, User


async def user_exists(username: str) -> bool:
    async with SessionLocal() as session:
        return session.query(User).filter_by(username=username).first() is not None


async def save_user(username: str, email: str, password_hash: str) -> None:
    async with SessionLocal() as session:
        new_user = User(username=username, email=email, password_hash=password_hash)
        session.add(new_user)
        session.commit()
