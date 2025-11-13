from sqlalchemy.future import select
from app.database.core.models import Image
from app.database.core.base import SessionLocal


async def download_image(filename: str, main_image: bool = False) -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(Image).where(Image.filename == filename))
        existing_image = result.scalar_one_or_none()

        if existing_image:
            print("❌ Зображення з такою назвою вже існує")
            return

        new_image = Image(filename=filename, main_image=main_image)
        session.add(new_image)
        await session.commit()


async def delete_image(filename: str) -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(Image).where(Image.filename == filename))
        image = result.scalars().one_or_none()
        await session.delete(image)
        await session.commit()


async def main_view():
    """Фунція яка відображує зображення в боту"""
    async with SessionLocal() as session:
        result = await session.execute(select(Image).order_by(Image.id.desc()).limit(1))
        last_image = result.scalar_one_or_none()
        if last_image:
            return last_image


async def get_images_with_main(filename: str = None):#!!!
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