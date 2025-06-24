from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.handlers.commands import cmd_start
from app.keyboards.students import get_week_selection_keyboard

router = Router()


@router.callback_query(F.data == "go_to_main_menu")
async def go_to_main_menu(callback: CallbackQuery):
    await callback.message.answer("/start")
    await callback.message.answer("🏠 *Ви повернулися в головне меню!*", parse_mode="Markdown")
    await cmd_start(callback.message)


@router.callback_query(F.data == "enroll_course")
async def enroll_course(callback: CallbackQuery):
    """Обробляє запит на запис до курсу."""
    await callback.message.answer("📍 Оберіть тиждень:", reply_markup=get_week_selection_keyboard())
