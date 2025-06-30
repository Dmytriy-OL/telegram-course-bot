from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.filters import StateFilter

from aiogram_calendar import SimpleCalendarCallback

from app.handlers.utils import delete_lesson_messages
from app.database.crud.lessons import get_lessons_for_teacher_and_optional_student
from app.database.core.models import LessonType
from app.handlers.utils import open_calendar, calendar, show_teacher_lessons
from app.handlers.teachers.view_lessons import format_lesson_text
from app.keyboards.teachers import confirm_lesson_keyboard, return_teacher_menu

router = Router()


@router.callback_query(F.data == "edit_lessons")
async def edit_lessons(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()


@router.callback_query(F.data == "delete_lesson_messages")
async def handle_delete_lesson_messages(callback: CallbackQuery, state: FSMContext):
    """Видаляє список повідомлень"""
    await delete_lesson_messages(callback, state)
