import os
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from app.images import BASE_DIR
from app.database.crud.users import set_user
from app.database.crud.images import main_view
from app.database.crud.admin import get_role
from app.keyboards.keyboards import get_admin_menu
from app.keyboards.teachers import get_teachers_command
from app.keyboards.students import get_student_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start_message(message: Message):
    """Обробляє команду старту від користувача."""
    await set_user(message.from_user.id, message.from_user.username, None, None)
    await cmd_start(message)


async def cmd_start(message: Message):
    """Обробляє команду старту від користувача."""
    last_image = await main_view()
    caption_text = (
        "<b>🎓 1. Ласкаво просимо до нашої школи англійської мови! 🌍</b>\n"
        "📖 - Ефективне навчання для всіх рівнів підготовки. ✨\n"
        "👨‍🏫 - Інтерактивні заняття з професійними викладачами. 🎯\n\n"
        "<b>🗣️ 2. Вчіть англійську легко та із задоволенням! 😃</b>\n"
        "🎯 - Індивідуальний підхід до кожного студента. 👥\n"
        "📝 - Сучасні методики навчання та розмовна практика. 🔥\n\n"
        "<b>🚀 3. Досягайте нових висот разом із нами! 🏆</b>\n"
        "📅 - Гнучкий графік занять, онлайн та офлайн курси. 💻\n"
        "🎓 - Підготовка до іспитів та кар'єрного зростання. 📈\n"
    )

    # Якщо немає зображення або воно не має імені файлу → надсилаємо тільки текст
    if not last_image or not last_image.filename:
        await message.answer("❌ Зображень немає в базі даних.")
        await message.answer(caption_text, parse_mode="HTML", reply_markup=get_student_main_menu())
        return
    last_image.filename += ".jpg"
    photo_path = os.path.join(BASE_DIR, last_image.filename)

    # Якщо файл зображення не знайдено → надсилаємо тільки текст
    if not os.path.exists(photo_path):
        last_image.filename += ".jpg"
        await message.answer("❌ Файл зображення не знайдено.")  # Спочатку повідомлення про помилку
        await message.answer(caption_text, parse_mode="HTML", reply_markup=get_student_main_menu())
        return

    # Відправка фото з підписом
    photo = FSInputFile(photo_path)
    await message.answer_photo(
        photo=photo, caption=caption_text,
        parse_mode="HTML", reply_markup=get_student_main_menu()
        )


@router.message(Command("admin"))
async def admin_command(message: Message):
    unknown = message.from_user.id
    admin = await get_role(unknown)

    if admin == "admin":
        await message.answer("🔧 *Панель адміністратора*", parse_mode="Markdown", reply_markup=get_admin_menu())
    else:
        await message.answer("🚫 У вас немає прав доступу.")


@router.message(Command("teacher"))
async def teacher_command(message: Message):
    unknown = message.from_user.id
    teacher = await get_role(unknown)

    if teacher in ("admin", "teacher"):
        await message.answer("🔧 *Панель викладача*", parse_mode="Markdown", reply_markup=get_teachers_command())
    else:
        await message.answer("🚫 У вас немає прав доступу.")


@router.message(F.text.casefold() == "/cancel")
async def cancel_any_operation(message: Message, state: FSMContext):
    """Скасовує операцію на будь-якому етапі"""
    teacher = await get_role(message.from_user.id)
    if teacher in ("admin", "teacher"):
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        await message.answer("🔧 *Панель викладача*", parse_mode="Markdown", reply_markup=get_teachers_command())
