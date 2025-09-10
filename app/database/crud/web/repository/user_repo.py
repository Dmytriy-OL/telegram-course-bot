from fastapi import Request

from sqlalchemy import update, delete, and_
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database.core.models import User, PendingUser, UserAvatar
from app.database.core.models import SessionLocal

from datetime import date


async def get_user_by_email(email: str) -> User | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User)
            .options(selectinload(User.avatar))  # підвантажуємо аватар
            .where(User.email == email)
        )
        user = result.scalars().first()
        return user


async def validate_user_unique(email: str, username: str) -> None:
    async with SessionLocal() as session:
        result_email = await session.execute(select(PendingUser).where((PendingUser.email == email)))
        if result_email.scalar_one_or_none():
            raise ValueError("Така електронна адреса вже існує!")

        # Перевірка username
        result_username = await session.execute(
            select(PendingUser).where((PendingUser.username == username)))
        if result_username.scalar_one_or_none():
            raise ValueError("Такий користувач вже існує!")


async def user_exists(email: str) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email, User.is_verified.is_(True)))
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


async def pending_user(email: str, username: str = None, password_hash: str = None, birth_date: date = None) -> None:
    async with SessionLocal() as session:
        await session.execute(delete(PendingUser).where(PendingUser.email == email))
        pending = PendingUser(email=email, username=username, password_hash=password_hash, birth_date=birth_date)
        session.add(pending)
        try:
            await session.commit()
        except Exception:
            raise ValueError("Така електронна адреса або логін уже в процесі підтвердження.")


async def confirm_email(email: str):
    async with SessionLocal() as session:
        result = await session.execute(select(PendingUser).where(PendingUser.email == email))
        pending = result.scalar_one_or_none()
        if not pending:
            raise ValueError("Користувач не знайдений або вже підтверджений")

        user = User(
            email=pending.email,
            username=pending.username,
            password_hash=pending.password_hash,
            birth_date=pending.birth_date,
            is_verified=True,
            terms_accepted=True
        )

        session.add(user)

        # Видаляємо з тимчасових
        await session.execute(delete(PendingUser).where(PendingUser.id == pending.id))

        await session.commit()


async def password_recovery(email: str, password: str):
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("Користувач не знайдений")
        user.password_hash = password
        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user


async def is_username_taken(username: str, current_email: str) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User.id).where(
                and_(
                    User.username == username,
                    User.email != current_email,  # виключаємо поточного користувача
                    User.is_verified.is_(True)
                )
            )
        )
        return result.scalar() is not None


async def update_user_data(email: str, name: str = None, surname: str = None, username: str = None,
                           birth_date: date = None) -> User:
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if name is not None:
            user.name = name
        if surname is not None:
            user.surname = surname
        if username is not None:
            user.username = username
        if birth_date is not None:
            user.birth_date = birth_date

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def update_user_avatar(user_id: int, file_name: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(UserAvatar).where(UserAvatar.user_id == user_id)
        )
        avatar = result.scalars().first()

        if avatar:
            # Якщо аватар існує — оновлюємо шлях
            avatar.file_path = file_name
        else:
            # Якщо аватара немає — створюємо новий
            avatar = UserAvatar(user_id=user_id, file_path=file_name)
            session.add(avatar)

        await session.commit()


async def fetch_updated_user_with_avatar(updated_user: User) -> User | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).options(selectinload(User.avatar)).where(User.id == updated_user.id)
        )
        updated_user = result.scalars().first()
        return updated_user
