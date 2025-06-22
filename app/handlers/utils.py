import os
from aiogram.types import Message, FSInputFile
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from app.database.crud import get_images_with_main
from app.images import BASE_DIR
from app.database.admin_crud import (get_enrollments_for_two_weeks, get_lessons_for_teacher_and_optional_student,
                                     get_teacher_by_telegram_id, remove_student_from_class)

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
