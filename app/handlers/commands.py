import os
# from app.image_uploads import BASE_DIR
from app.images import BASE_DIR
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from app.database.crud import get_images_with_main, view_user, delete_image_from_db, set_user, main_view
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.keyboards.keyboards import get_inline_keyboard, get_admin_main_menu, get_teachers_command
from app.database.admin_crud import get_role

router = Router()


@router.message(CommandStart())
async def cmd_start_message(message: Message):
    """Обробляє команду старту від користувача."""
    await set_user(message.from_user.id, message.from_user.username, None, None, None)
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
        await message.answer(caption_text, parse_mode="HTML", reply_markup=get_inline_keyboard())
        return
    last_image.filename += ".jpg"
    photo_path = os.path.join(BASE_DIR, last_image.filename)

    # Якщо файл зображення не знайдено → надсилаємо тільки текст
    if not os.path.exists(photo_path):
        last_image.filename += ".jpg"
        await message.answer("❌ Файл зображення не знайдено.")  # Спочатку повідомлення про помилку
        await message.answer(caption_text, parse_mode="HTML", reply_markup=get_inline_keyboard())
        return

    # Відправка фото з підписом
    photo = FSInputFile(photo_path)
    await message.answer_photo(photo=photo, caption=caption_text, parse_mode="HTML", reply_markup=get_inline_keyboard())


@router.message(Command("admin"))
async def admin_command(message: Message):
    unknown = message.from_user.id
    admin = await get_role(unknown)

    if admin == "admin":
        await message.answer("🔧 *Панель адміністратора*", parse_mode="Markdown", reply_markup=get_admin_main_menu())
    else:
        await message.answer("🚫 У вас немає прав доступу.")


@router.message(Command("teacher"))
async def teacher_command(message: Message):
    unknown = message.from_user.id
    teacher = await get_role(unknown)

    if teacher in ("admin", "teacher"):
        await message.answer("🔧 *Панель адміністратора*", parse_mode="Markdown", reply_markup=get_teachers_command())
    else:
        await message.answer("🚫 У вас немає прав доступу.")
