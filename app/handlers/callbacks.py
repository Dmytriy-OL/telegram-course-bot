from aiogram import Bot, types, F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from app.database.crud import find_activities_by_date, enroll_student_to_lesson, set_user, lesson_records_display, \
    cancel_record_db
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.keyboards.keyboards import back_button_markup
from app.handlers.commands import cmd_start
from app.handlers.utils import delete_previous_message

# Створюємо роутер
router = Router()


class Form(StatesGroup):
    waiting_full_name = State()
    waiting_confirmation = State()
    waiting_user_id = State()


def generate_week_keyboard(offset=0):
    """Генерує клавіатуру для вибору дня тижня з урахуванням зміщення (offset)."""
    keyboard = InlineKeyboardBuilder()
    days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]

    today = datetime.today()
    current_weekday = today.weekday()

    for i in range(7):
        date = today + timedelta(days=(i - current_weekday + offset))
        day_text = f"{days[i]} {date.day}.{date.month}.{date.year}"
        callback_data = f"select_day_{i}_{date.day}_{date.month}_{date.year}"
        keyboard.add(InlineKeyboardButton(text=day_text, callback_data=callback_data))

    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message"))
    return keyboard.adjust(1).as_markup()


@router.callback_query(F.data.startswith("select_day_"))
async def select_day(callback: CallbackQuery):
    """Виводить заняття"""
    days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]

    _, _, day_index, day, month, year = callback.data.split("_")
    day_index = int(day_index)
    selected_day = days[day_index]

    lessons = await find_activities_by_date(int(year), int(month), int(day))

    if lessons:
        for lesson in lessons:
            teacher = lesson.administrator
            teacher_fullname = f"{teacher.name} {teacher.surname}" if teacher else "Невідомо"
            lesson_text = (
                f"📅 *Ви вибрали:* *{selected_day}, {day}.{month}.{year}*\n\n"
                f"📖 *{lesson.title}*\n"
                f"🕒 *Час:* {lesson.datetime.strftime('%H:%M')}\n"
                f"📌 *Тип заняття:* {lesson.type_lesson}\n"
                f"👤 *Викладач:* {teacher_fullname}\n"
                f"🎫 *Доступно місць:* {lesson.places}\n\n"
            )

            # Якщо місця немає
            if not lesson.freely:
                lesson_text += (
                    '🔴 *Місця на заняття більше не доступні.Дочекайтеся, '
                    'поки хтось відмовиться або адміністратор додасть місце.* '
                    '🧐\n_Слідкуйте за оновленнями!_ 🔔'
                )
                await callback.message.answer(lesson_text, parse_mode="Markdown", reply_markup=back_button_markup())
                continue  # Переходимо до наступного заняття

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text="✅ Записатися",
                                         callback_data=f"recording_day_{lesson.id}_{lesson.places}")
                ], [
                    InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message")
                ]]
            )
            await callback.message.answer(lesson_text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await callback.message.answer("❌ *Занять на цей день немає або їх ще не додали.*", parse_mode="Markdown",
                                      reply_markup=back_button_markup())


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

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="📅 Обрати інше заняття", callback_data="enroll_course")
        ], [
            InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_to_main_menu")
        ]]
    )

    await message.answer(text_result, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "go_to_main_menu")  # !!!!
async def go_to_main_menu(callback: CallbackQuery):
    await callback.message.answer("/start")
    await callback.message.answer("🏠 *Ви повернулися в головне меню!*", parse_mode="Markdown")
    await cmd_start(callback.message)


@router.message(F.text.lower() == "/ok")
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
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="📅 Виконати ще один запис", callback_data="enroll_course")
        ], [
            InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_to_main_menu")
        ]]
    )

    await message.answer(f"✅ {last_name} {first_name}, ви успішно записані на заняття!", parse_mode="Markdown",
                         reply_markup=keyboard)
    await state.clear()


@router.message(F.text.lower() == "/again")
async def restart_registration(message: Message, state: FSMContext):
    await message.answer("🔄 Введіть ваше прізвище та ім'я ще раз:")
    await state.set_state(Form.waiting_full_name)  # Повертаємо стан назад


@router.callback_query(F.data == "select_this_week")
async def select_this_week(callback: CallbackQuery):
    """Відправляє клавіатуру для поточного тижня."""
    await callback.message.answer("📅 Оберіть день:", reply_markup=generate_week_keyboard())


@router.callback_query(F.data == "select_next_week")
async def select_next_week(callback: CallbackQuery):
    """Відправляє клавіатуру для наступного тижня."""
    await callback.message.answer("📅 Оберіть день:", reply_markup=generate_week_keyboard(offset=7))


@router.callback_query(F.data == "enroll_course")
async def enroll_course(callback: CallbackQuery):
    """Обробляє запит на запис до курсу."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Записатися на цей тиждень 🔥", callback_data="select_this_week")],
        [InlineKeyboardButton(text="😃 Записатися на наступний тиждень 😃", callback_data="select_next_week")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message")]
    ])
    await callback.message.answer("📍 Оберіть тиждень:", reply_markup=keyboard)


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
        user = record.user
        text_result = (
            "🎓 *Ваші активні записи на заняття:*\n\n"
            f"📌 *Курс:* {lesson.title}\n"
            f"👨‍🏫 *Викладач:* {lesson.instructor}\n"
            f"📅 *Дата та час:* {lesson.datetime.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"🧑‍🎓 *Студент:* {user.name or 'Невідомо'} {user.surname or 'Невідомо'}\n"
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


@router.callback_query(F.data == "remove_prev_message")
async def remove_prev_message(callback: CallbackQuery, state: FSMContext):
    """Видаляє попереднє повідомлення."""
    await delete_previous_message(callback, state)
