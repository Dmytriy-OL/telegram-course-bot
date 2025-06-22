from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database.crud import lesson_records_display, cancel_record_db

router = Router()


@router.callback_query(F.data == "my_bookings")
async def my_bookings(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_tg_id = callback.from_user.id
    records = await lesson_records_display(user_tg_id)
    if not records:
        await callback.message.answer("❌ У вас немає активних записів.")
        return

    for record in records:
        lesson = record.lesson
        teacher = lesson.administrator
        full_name = record.full_name
        text_result = (
            "🎓 *Ваші активні записи на заняття:*\n\n"
            f"📌 *Курс:* {lesson.title}\n"
            f"👨‍🏫 *Викладач:* {teacher.name} {teacher.surname}\n"
            f"📅 *Дата та час:* {lesson.datetime.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"🧑‍🎓 *Студент:* {full_name or 'Невідомо'}\n"
            "--------------------------------------\n"
            "🔔 *Якщо не зможете відвідати заняття, будь ласка, скасуйте запис.*\n"
            "❌ Натисніть кнопку нижче, щоб скасувати запис.\n"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Скасувати запис", callback_data=f"cancel_confirmed_{record.id}")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message")]])
        await callback.message.answer(text_result, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data.startswith("cancel_confirmed_"))
async def ask_cancel_confirmation(callback: CallbackQuery, state: FSMContext):
    record_id = callback.data.split("_")[-1]
    await state.update_data(record_id=record_id)
    text_result = (
        "*Ви впевнені що хочете відмінити запис*\n\n"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Так", callback_data=f"cancel_lesson")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message")]])
    await callback.message.answer(text_result, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "cancel_lesson")
async def cancel_record(callback: CallbackQuery, state: FSMContext):
    record = await state.get_data()
    record_id = record.get("record_id")
    record = await cancel_record_db(int(record_id))
    if record:
        lesson = record.lesson
        text_result = (
            "❌ *Ваший запис на заняття скасовано:❌*\n\n"
            f"📌 *Курс:* {lesson.title}\n"
            f"📅 *Дата та час:* {lesson.datetime.strftime('%Y-%m-%d %H:%M')}\n\n"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Головне меню", callback_data=f"go_to_main_menu")],
                [InlineKeyboardButton(text="🔄 Обновити записи", callback_data="my_bookings")]])
        await callback.message.answer(text_result, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await callback.answer("Цей запис вже видалений❌")
    await state.clear()
