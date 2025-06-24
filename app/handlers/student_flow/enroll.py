from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.database.crud.lessons import enroll_student_to_lesson
from app.database.crud.users import set_user
from app.handlers.utils import delete_previous_message
from app.keyboards.students import get_successful_enrollment_keyboard, get_cancel_operation_keyboard

router = Router()


class Form(StatesGroup):
    waiting_full_name = State()
    waiting_confirmation = State()


@router.callback_query(F.data.startswith("recording_day_"))
async def select_day(callback: CallbackQuery, state: FSMContext):
    _, _, lesson_id, lesson_users = callback.data.split("_")
    lesson_id = int(lesson_id)
    number_of_students = int(lesson_users)
    if number_of_students >= 1:
        await state.update_data(lesson_id=lesson_id)
        text_example = (
            f"📝*Напишіть ваше прізвище та імя:*\n"
            f"Наприклад:Олійник Дмитрій\n"
        )
        await callback.message.answer(text_example, parse_mode="Markdown")
        await state.set_state(Form.waiting_full_name)
    else:
        await callback.message.answer("Записи недоступні немає мість:", callback_data=remove_prev_message)


@router.message(Form.waiting_full_name)
async def process_first_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    if " " in full_name:  # Перевіряємо, чи є пробіл між прізвищем та ім'ям
        last_name, first_name = full_name.split(" ", 1)
        text_result = (
            f"📝 <b>Запис на заняття:</b>\n"
            f"👤 Учень: {last_name} {first_name}\n\n"
            f"✅ Якщо все вірно, натисніть /OK\n"
            f"🔄 Якщо потрібно змінити дані, натисніть /again\n"
            f"❌ Щоб <b>скасувати запис</b>, натисніть /cancel_operation\n"
        )
        await message.answer(text_result, parse_mode="HTML")

        await state.update_data(first_name=first_name, last_name=last_name, full_name=full_name)  # Зберігаємо дані
        await state.set_state(Form.waiting_confirmation)
    else:
        await message.answer("❌ Будь ласка, введіть ім'я та прізвище через пробіл.")


@router.message(Form.waiting_confirmation, F.text.lower() == "/again")
async def restart_registration(message: Message, state: FSMContext):
    await message.answer("🔄 Введіть ваше прізвище та ім'я ще раз:")
    await state.set_state(Form.waiting_full_name)


@router.message(Form.waiting_confirmation, F.text.lower() == "/ok")
async def confirm_registration(message: Message, state: FSMContext):
    user_data = await state.get_data()
    first_name = user_data.get("first_name")
    last_name = user_data.get("last_name")
    lesson_id = user_data.get("lesson_id")
    full_name = user_data.get("full_name")

    if not first_name or not last_name:  # Якщо користувач просто так натисне не в стані
        await message.answer("❌ Ви не перебуваєте в процесі запису.")
        return

    await set_user(message.from_user.id, message.from_user.username, first_name, last_name)
    await enroll_student_to_lesson(lesson_id, message.from_user.id, full_name)
    await message.answer(f"✅ {last_name} {first_name}, ви успішно записані на заняття!", parse_mode="Markdown",
                         reply_markup=get_successful_enrollment_keyboard())
    await state.clear()


@router.message(F.text.lower() == "/cancel_operation")
async def cancel_save(message: Message, state: FSMContext):
    await state.clear()

    text_result = (
        "❌ *Запис скасовано!* ❌\n\n"
        "😔 *Шкода, що ви передумали... Але ви завжди можете повернутися!* 🎯\n\n"
        "📌 *Що далі?*\n"
        "🔹 *Обрати інше заняття* – натисніть кнопку нижче 📅\n"
        "🔹 *Повернутися в головне меню* – натисніть 🏠\n\n"
        "✨ _Можливо, на вас чекає щось ще цікавіше!_ 😉"
    )

    await message.answer(text_result, parse_mode="Markdown", reply_markup=get_cancel_operation_keyboard())


@router.callback_query(F.data == "remove_prev_message")
async def remove_prev_message(callback: CallbackQuery, state: FSMContext):
    """Видаляє попереднє повідомлення."""
    await delete_previous_message(callback, state)
