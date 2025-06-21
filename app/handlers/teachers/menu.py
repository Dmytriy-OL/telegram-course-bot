from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from app.handlers.utils import delete_previous_message
from app.keyboards.teachers import teacher_main_menu, get_teachers_command

router = Router()


@router.callback_query(F.data == "teachers")
async def teachers(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.delete()

    await callback.message.answer(
        "👩‍🏫 *Меню викладача*\n\n"
        "Оберіть дію, яку бажаєте виконати зі списку нижче 👇",
        parse_mode="Markdown",
        reply_markup=teacher_main_menu()
    )


@router.callback_query(F.data == "teacher_menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        text="Оберіть дію з меню адміністратора:",
        reply_markup=get_teachers_command()
    )


@router.callback_query(F.data == "back_to_teacher_menu")
async def delete_message_handler(callback: CallbackQuery, state: FSMContext):
    await delete_previous_message(callback, state)
