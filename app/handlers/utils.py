import os
import asyncio
from aiogram.types import Message, FSInputFile
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup

from aiogram_calendar import SimpleCalendar
from app.database.crud.images import get_images_with_main
from app.images import BASE_DIR

from app.database.crud.admin import get_teacher_by_telegram_id
from app.database.crud.lessons import get_lessons_for_teacher_and_optional_student

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


async def open_calendar() -> InlineKeyboardMarkup:
    """Відкриває inline-календар"""
    return await calendar.start_calendar()


async def show_teacher_lessons(callback: CallbackQuery):
    tg_id = callback.from_user.id
    teacher = await get_teacher_by_telegram_id(tg_id)
    lessons = await get_lessons_for_teacher_and_optional_student(teacher.id)
    return teacher, lessons


async def delete_lesson_messages(callback: CallbackQuery, state: FSMContext):
    """Асинхронно видаляє список повідомлень"""
    await callback.answer()

    data = await state.get_data()
    message_ids = data.get("lesson_message_ids", [])

    delete_tasks = []
    for msg_id in message_ids:
        delete_tasks.append(
            callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
        )

    try:
        await asyncio.gather(*delete_tasks, return_exceptions=True)
    except Exception as e:
        print(f"❗️Помилка при одночасному видаленні: {e}")

    await state.clear()


