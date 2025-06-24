from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.database.core.models import Image, SessionLocal
import asyncio
import os
import shutil  # Додаємо shutil для копіювання файлів
from app.database.admin_crud import download_image,delete_image
from app.images import BASE_DIR


async def save_image_to_disk_and_db(file_bytes, title: str, main_image: bool = False):
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    file_path = BASE_DIR / f"{title}.jpg"

    with open(file_path, "wb") as f:
        f.write(file_bytes.read())

    await download_image(title, main_image)


async def delete_image_to_disk_and_db(filename: str):
    file_path = BASE_DIR / f"{filename}.jpg"

    if file_path.exists():
        os.remove(file_path)

    await delete_image(filename)


async def add_image(session: AsyncSession, filename: str, mimetype: str):
    """Функція для додавання нового зображення з обмеженням у 2 записи"""

    # Отримуємо кількість записів у таблиці
    result = await session.execute(select(Image))
    images = result.scalars().all()

    if len(images) >= 2:
        print("❌ Немає можливості додати більше 2 зображень!")
        return None  # Не додаємо зображення

    # Якщо зображень менше двох — додаємо
    new_image = Image(filename=filename, mimetype=mimetype)
    session.add(new_image)
    await session.commit()
    print(f"✅ Зображення '{filename}' додано успішно!")
    return new_image


async def upload_image(filename: str, mimetype: str) -> int | None:
    async with SessionLocal() as session:
        try:
            image = Image(filename=filename, mimetype=mimetype)
            session.add(image)
            await session.commit()
            return image.id
        except IntegrityError:
            await session.rollback()
            print("❌ Помилка: файл уже існує або некоректні дані")
            return None


async def get_image(image_id: int) -> Image | None:
    async with SessionLocal() as session:
        result = await session.execute(select(Image).where(Image.id == image_id))
        image = result.scalar_one_or_none()
        if image:
            print(f"✅ Зображення знайдено: {image.filename}")
        else:
            print("❌ Зображення не знайдено в базі")
        return image


async def main():
    """
    Основна функція для тестування завантаження та отримання зображень.
    """
    image_dir = "../images"  # Директорія, де зберігаються вихідні зображення
    upload_dir = "../image_uploads"  # Директорія для збережених копій
    image_filename = "Courges.jpg"  # Назва файлу

    image_path = os.path.join(image_dir, image_filename)  # Повний шлях до вихідного файлу

    # 🔹 Перевіряємо, чи файл існує
    if not os.path.exists(image_path):
        print(f"❌ Файл {image_path} не знайдено!")
        return

    # 🔹 Завантажуємо інформацію про зображення в базу
    image_id = await upload_image(image_filename, "image/jpeg")

    if image_id:
        print(f"✅ Зображення завантажено з ID: {image_id}")
    else:
        print("❌ Не вдалося завантажити зображення")
        return

    # 🔹 Отримуємо інформацію про зображення за ID
    image = await get_image(image_id)

    if image:
        output_path = os.path.join(upload_dir, image.filename)  # Куди копіювати файл

        # 🔹 Копіюємо файл в нове місце
        shutil.copy(image_path, output_path)
        print(f"✅ Зображення збережено як {output_path}")
    else:
        print("❌ Зображення не знайдено або дані порожні")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        print("⚠ Неможливо викликати asyncio.run() в уже запущеному event loop.")