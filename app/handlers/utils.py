from aiogram.types import Message, FSInputFile
from app.database.crud import get_images_with_main
from app.images import BASE_DIR
# from app.image_uploads import BASE_DIR
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

calendar = SimpleCalendar()


async def display_images(message: Message, text: str = 'Передай текст', send_photos: bool = False):
    images, image = await get_images_with_main()
    if images:
        await message.answer("Всі зображення з бази данних:")
        for index, img in enumerate(images, start=1):
            caption = f"Зображення #{index}: `{img.filename}`"
            if img == image:
                caption += " - Стоїть на заставці"

            if send_photos:
                photo_path = os.path.join(BASE_DIR, img.filename)
                photo = FSInputFile(photo_path)
                await message.answer_photo(photo=photo, caption=caption)
            else:
                await message.answer(text=caption, parse_mode="Markdown")
        await message.answer(text)
    else:
        await message.answer("❌ Зображення не знайдено.")


async def delete_previous_message(callback: CallbackQuery, state: FSMContext):
    """Видаляє попереднє повідомлення та очищує state."""
    await state.clear()
    await callback.message.delete()


async def open_calendar():
    return await calendar.start_calendar()

