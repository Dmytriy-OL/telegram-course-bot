from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

from app.handlers.commands import cmd_start

router = Router()


@router.callback_query(F.data == "go_to_main_menu")
async def go_to_main_menu(callback: CallbackQuery):
    await callback.message.answer("/start")
    await callback.message.answer("🏠 *Ви повернулися в головне меню!*", parse_mode="Markdown")
    await cmd_start(callback.message)


@router.callback_query(F.data == "enroll_course")
async def enroll_course(callback: CallbackQuery):
    """Обробляє запит на запис до курсу."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Записатися на цей тиждень 🔥", callback_data="select_this_week")],
        [InlineKeyboardButton(text="😃 Записатися на наступний тиждень 😃", callback_data="select_next_week")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message")]
    ])
    await callback.message.answer("📍 Оберіть тиждень:", reply_markup=keyboard)
