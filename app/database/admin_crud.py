import asyncio
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

from app.database.models import SessionLocal, User, Image, Caption, Lesson, LessonType, Enrollment, Administrator


async def add_admin(tg_id: int, name: str, surname: str, login: str, main_admin: bool = False):
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


async def view_users(unknown: bool = False):
    async with SessionLocal() as session:
        if unknown:
            result = await session.execute(select(User).where(User.name == "Null"))
            users = result.scalars().all()
        else:
            result = await session.execute(select(User))
            users = result.scalars().all()
        return users


async def add_caption(title: str, caption: str, main: bool) -> tuple[int | None, str]:
    async with SessionLocal() as session:
        result = await session.execute(select(Caption).where(Caption.title == title))
        existing_caption = result.scalars().first()

        if existing_caption:
            print(f"❌ Заголовок '{title}' вже існує. Запис не додано.")
            return None, f"❌ Заголовок '{title}' вже існує. Запис не додано."

        # Перевіряємо, чи вже є головний заголовок
        main_result = await session.execute(select(Caption).where(Caption.main == True))
        main_caption = main_result.scalars().first()

        if main_caption and main:  # Якщо є головний і новий теж має main=True
            warning_msg = f"⚠️ В базі вже є головний заголовок ('{main_caption.title}'). Новий запис буде 'main=False'."
            print(f"⚠️ В базі вже є головний заголовок ('{main_caption.title}'). Новий запис буде 'main=False'.")
            main = False  # Автоматично змінюємо main на False
        else:
            warning_msg = ""

        # Додаємо новий запис
        new_caption = Caption(title=title, caption=caption, main=main)
        session.add(new_caption)
        await session.commit()
        await session.refresh(new_caption)

        success_msg = f"✅ Текст '{title}' успішно додано!"
        return new_caption.id, f"{warning_msg}\n{success_msg}".strip()


async def get_all_captions():
    async with SessionLocal() as session:
        result = await session.execute(select(Caption))
        text = result.scalars().all()
        if text:
            for tx in text:
                if tx.main:
                    print(f"Заголовок:{tx.title}-Головний\nТекст:{tx.caption}")
                else:
                    print(f"Заголовок:{tx.title}\nТекст:{tx.caption}")
            return text
        else:
            print("❌ Тексту і заголовку немає.")
            return None


async def main_captions_switch(title: str):
    async with SessionLocal() as session:
        # Отримуємо всі записи
        result = await session.execute(select(Caption))
        text_result = result.scalars().all()
        warning_msg = ""
        # Шукаємо поточний головний запис
        current_main = next((text for text in text_result if text.main), None)
        new_main = next((text for text in text_result if text.title == title), None)

        if not new_main:
            warning_msg += "❌ Текст із таким заголовком не знайдено."
            print("❌ Текст із таким заголовком не знайдено.")
            return warning_msg

        if new_main.main:
            warning_msg += "✅ Цей текст уже є головним!"
            print("✅ Цей текст уже є головним!")
            return warning_msg

        # Скидаємо попередній головний запис (якщо є)
        if current_main:
            current_main.main = False

        # Робимо новий запис головним
        new_main.main = True
        await session.commit()

        print(f"🎉 Тепер '{title}' є головним текстом!")
        warning_msg += f"🎉 Тепер '{title}' є головним текстом!"
        return warning_msg


async def delete_captions(title: str) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(select(Caption).where(Caption.title == title))
        existing_caption = result.scalars().first()
        if not existing_caption:
            print(f"❌ Заголовок '{title}' не знайдено.")
            return False  # Повертаємо False, якщо запис не знайдено

        await session.delete(existing_caption)
        await session.commit()
        print(f"✅ Заголовок '{title}' видалено.")
        return True  # Повертаємо True, якщо запис успішно видалено


async def download_image(filename: str, main_image: bool = False):
    async with SessionLocal() as session:
        result = await session.execute(select(Image).where(Image.filename == filename))
        existing_image = result.scalar_one_or_none()

        if existing_image:
            print("❌ Зображення з такою назвою вже існує")
            return

        new_image = Image(filename=filename, main_image=main_image)
        session.add(new_image)
        await session.commit()


async def view_image():
    async with SessionLocal() as session:
        result = await session.execute(select(Image))
        images = result.scalars().all()
        if not images:
            print("❌ Зображень не має")
            return
        return images


async def delete_image(filename: str):
    async with SessionLocal() as session:
        result = await session.execute(select(Image).where(Image.filename == filename))
        image = result.scalars().one_or_none()
        await session.delete(image)
        await session.commit()


async def main_image_switch(filename: str):
    async with SessionLocal() as session:
        result = await session.execute(select(Image))
        images_result = result.scalars().all()
        warning_img = ""
        # Шукаємо поточний головний запис
        current_main = next((image for image in images_result if image.main_image), None)
        new_main = next((image for image in images_result if image.filename == filename), None)

        if not new_main:
            warning_img += "❌ Зображення із таким заголовком не знайдено."
            print("❌ Зображення із таким заголовком не знайдено.")
            return warning_img

        if new_main.main_image:
            warning_img += "✅ Це зображення уже є головним!"
            print("✅ Це зображення уже є головним!")
            return warning_img

        # Скидаємо попередній головний запис (якщо є)
        if current_main:
            current_main.main_image = False

        new_main.main_image = True

        await session.commit()

        warning_img += f"🎉 Зображення `{filename}` стало головним!"
        return warning_img


async def get_enrollments_for_two_weeks():
    async with SessionLocal() as session:
        today = datetime.today()
        weekday = today.weekday()  # 0 = Monday

        this_monday = today - timedelta(days=weekday)
        next_sunday = this_monday + timedelta(days=13)

        result = await session.execute(
            select(Enrollment)
            .join(Enrollment.lesson)
            .options(joinedload(Enrollment.lesson), joinedload(Enrollment.user))
            .where(Lesson.datetime >= this_monday)
            .where(Lesson.datetime <= next_sunday)
        )

        enrollments = result.scalars().all()

        return enrollments


async def active_courses_for_two_weeks():
    async with SessionLocal() as session:
        today = datetime.today()
        weekday = today.weekday()  # 0 = Monday

        this_monday = today - timedelta(days=weekday)
        next_sunday = this_monday + timedelta(days=13)

        result = await session.execute(
            select(Lesson)
            .where(Lesson.datetime >= this_monday)
            .where(Lesson.datetime <= next_sunday)
            # .where(Lesson.places >= 1)
        )

        lessons = result.scalars().all()
        return lessons


async def main():
    enrollments = await get_enrollments_for_two_weeks()
    for enrollment in enrollments:
        print(
            f"👤 {enrollment.user.name} {enrollment.user.surname} записаний на курс: {enrollment.lesson.title} — {enrollment.lesson.datetime}")


if __name__ == '__main__':
    # asyncio.run(main())
    # print(asyncio.run(get_role(974638427)))
    asyncio.run(add_admin(974638427, "Саша", "Олійник", "dimon20012", False))
    # asyncio.run(view_admins())
