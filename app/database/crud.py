import asyncio
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.database.models import SessionLocal, User, Image, Caption, Lesson, LessonType, Enrollment
from aiogram.fsm.context import FSMContext
from sqlalchemy.sql.expression import or_, and_
# from app.image_uploads import BASE_DIR
from app.images import BASE_DIR
from datetime import datetime
import os


async def delete_image_from_db(filename: str = None, id_img: int = None):
    """Функція для видалення зображення"""
    if isinstance(filename, int) and id_img is None:
        id_img = filename
        filename = None

    async with SessionLocal() as session:
        if filename is None and id_img is None:
            return False, "❌ Треба вказати або filename, або id_img!"

        result = await session.execute(
            select(Image).where(or_(Image.filename == filename, Image.id == id_img))
        )
        image = result.scalar_one_or_none()

        if image:
            file_path = os.path.join(BASE_DIR, image.filename)

            # Видаляємо запис з БД
            await session.delete(image)
            await session.commit()

            # Видаляємо файл, якщо він існує
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, f"Зображення {image.filename} видалено з бази та файлової системи!"
            else:
                return True, f"Зображення {image.filename} видалено з бази, але файл не знайдено!"
        else:
            return False, " Зображення не знайдено!"


async def get_images_with_main(filename: str = None):
    """Фунція для пошуку і відображення зображення з головним на заставці"""
    async with SessionLocal() as session:
        if filename:
            result = await session.execute(select(Image).where(Image.filename == filename))
            image = result.scalar_one_or_none()
            if image:
                print(f"✅ Зображення {image.filename} знайдено!")
                return [image], None
            else:
                print("❌ Зображення не знайдено, можливо, ви ввели неправильне ім'я.")
                return [], None
        else:
            result = await session.execute(select(Image))
            images = result.scalars().all()
            if images:
                for img in images:
                    print(f"✅ Зображення {img.filename} знайдено!")
                print(f"☑️ Останнє зображення: {img.filename}")
                return images, img
            else:
                print("❌ Немає жодних зображень у базі даних.")
                return [], None


async def main_view():
    """Фунція яка відображує зображення в боту"""
    async with SessionLocal() as session:
        result = await session.execute(select(Image).order_by(Image.id.desc()).limit(1))
        last_image = result.scalar_one_or_none()
        if last_image:
            return last_image


async def view_user(name: str = None):
    """Фунція для відображення користувачів"""
    async with SessionLocal() as session:
        # Виконуємо запит до бази даних
        result = await session.execute(select(User))
        # Отримуємо одного користувача (якщо він є)
        users = result.scalars().all()
        if users:
            for user in users:
                print(f"Знайдено користувача: {user.name}")  # Виводимо ім'я знайденого користувача
            return users  # Повертаємо одного користувача
        else:
            print("❌ Користувач не знайдений.")
            return None  # Повертаємо None, якщо користувач не знайдений


async def add_user(name: str = "Дімас", surname: str = 'Олійник', login: str = "ddiii") -> int | None:
    """Фунція для додавання користувача в бд"""
    async with SessionLocal() as session:
        user = User(name=name, surname=surname, login=login)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user.id


async def create_lesson(title: str, teacher: str, year: int, month: int, day: int, hour: int, minute: int,
                        type_lesson: LessonType,
                        places: int, freely: bool = True):
    async with SessionLocal() as session:
        lesson_datetime = datetime(year, month, day, hour, minute)
        lesson = Lesson(
            title=title,
            instructor=teacher,
            datetime=lesson_datetime,
            type_lesson=type_lesson,
            freely=freely,
            places=places
        )
        session.add(lesson)
        await session.commit()  # Фіксуємо зміни в базі
        print("📌 Заняття додано в базу!")
        await session.refresh(lesson)  # Оновлюємо об'єкт з БД
        return lesson  # Повертаємо створений об'єкт


async def view_lesson():
    async with SessionLocal() as session:
        result = await session.execute(select(Lesson))
        all_lessons = result.scalars().all()

        print("📚 Список занять:")
        if all_lessons:
            for lesson in all_lessons:
                print(
                    f"🔹 Назва: {lesson.title},Кільість мість: {str(lesson.places)}")
        else:
            print("Заннять немає")


async def find_activities_by_date(year: int, month: int, day: int):
    async with SessionLocal() as session:
        start_date = datetime(year, month, day, 0, 0, 0)
        end_date = datetime(year, month, day, 23, 59, 59)
        print(f"Шукаємо заняття від {start_date} до {end_date}")
        result = await session.execute(
            select(Lesson).where(and_(Lesson.datetime >= start_date, Lesson.datetime <= end_date)))
        lessons = result.scalars().all()
        if lessons:
            for lesson in lessons:
                lesson.type_lesson = "Онлайн" if lesson.type_lesson == LessonType.ONLINE else "Офлайн"
                print(f"Заняття: {lesson.title}\nЧас: {lesson.datetime}\nТип: {lesson.type_lesson}")
            return lessons
        else:
            print("Заняття на цей день відсутні")
            return []


async def set_user(tg_id: int, login: str, number: str, name: str = None, surname: str = None):
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            user = User(tg_id=tg_id, name=name, surname=surname, login=login, number=number)
            session.add(user)
        else:
            if name is None or surname is None:
                user.login = login
                user.number = number
            else:
                user.name = name
                user.surname = surname
                user.login = login
                user.number = number

        await session.commit()
        await session.refresh(user)
        return user


async def lesson_records_display(tg_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Enrollment).where(Enrollment.user_id == tg_id).options(joinedload(Enrollment.lesson),
                                                                          joinedload(Enrollment.user))
        )
        records = result.scalars().all()

        if records:
            for entry in records:
                lesson = entry.lesson  # Доступ до повної інформації про заняття
                user = entry.user
                print(f"Запис: {lesson.title}\nДата: {lesson.datetime}записаний {user.name} {user.surname}")
        else:
            print("У вас немає записів")
        return records


async def enroll_student_to_lesson(lesson_id: int, user_tg_id: int):
    async with SessionLocal() as session:
        enrollment = Enrollment(user_id=user_tg_id, lesson_id=lesson_id)
        result = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = result.scalar_one_or_none()
        if lesson:
            if lesson.places > 0:
                lesson.places -= 1
                if lesson.places == 0:
                    lesson.freely = False
            else:

                return "Місця на заняття більше не доступні."
        session.add(enrollment)

        await session.commit()
        # await session.refresh(lesson)
        # return "Запис успішно здійснений!"


async def cancel_record_db(lesson_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Enrollment).where(Enrollment.id == lesson_id).options(joinedload(Enrollment.lesson))
        )
        record = result.scalars().first()
        if record:
            lesson = record.lesson
            print(f"Запис {lesson.title},скасовоно")
            lesson.places += 1
            await session.delete(record)
            if not lesson.freely:
                lesson.freely = True

            await session.commit()
            return record
        else:
            print("Запис ненайдено")
        return None



async def main():
    # await create_lesson("Для студентів", "Олексіївна А.В", 2025, 3, 23, 18, 30, LessonType.ONLINE, True, )
    await create_lesson("Дорослі", "Олексіївна А.В", 2025, 5, 15, 18, 30, LessonType.ONLINE, 1, True)

    print("___________________")
    await view_lesson()

    # await add_caption("Чоловічі курси", "✅ - Ефективне навчання для всіх рівнів підготовки.", True)
    # await delete_captions("Дитячі курси")
    # await get_all_captions()
    # await main_captions_switch("Чоловічі курси")
    # await get_all_captions()


if __name__ == '__main__':
    pass
    # print("\033[93m⚠️ Операцію скасовано\033[0m")
    # print("\033[91mПомилка!\033[0m")
    # print("\033[92m✅ Успіх!\033[0m")
    # asyncio.run(cancel_record(1))
    # asyncio.run(lesson_records_display(974638427))
    # asyncio.run(find_activities_by_date(2025, 3, 23))
    # asyncio.run(main())
    # asyncio.run(view_image("Courges.jpg"))
    # asyncio.run(add_user())
    # asyncio.run(main())
    # asyncio.run((view_user()))
    # asyncio.run(view_image()
