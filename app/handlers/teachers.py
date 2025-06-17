from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.filters import StateFilter

from aiogram_calendar import SimpleCalendarCallback

from app.database.admin_crud import (get_enrollments_for_two_weeks, get_lessons_for_teacher_and_optional_student,
                                     get_teacher_by_telegram_id, remove_student_from_class)
from app.database.crud import create_lesson, cancel_record_db
from app.database.models import LessonType
from app.handlers.utils import open_calendar, calendar, delete_previous_message,show_teacher_lessons
from app.keyboards.keyboards import back_button_builder, get_teachers_command

router = Router()


class LessonFactory(StatesGroup):
    waiting_for_title = State()
    waiting_for_date = State()
    waiting_for_manual_date = State()
    waiting_for_time = State()
    waiting_for_type = State()
    waiting_for_places = State()


@router.callback_query(F.data == "teachers")
async def teachers(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.delete()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🆕 Додати заняття", callback_data="add_lesson")],
            [InlineKeyboardButton(text="📥 Заняття та записи", callback_data="lessons_and_signups")],
            [InlineKeyboardButton(text="✏️ Редагувати заняття", callback_data="edit_lessons")],
            [InlineKeyboardButton(text="🔗 Додати посилання на заняття", callback_data="lesson_link")],
            [InlineKeyboardButton(text="🔙 Повернутись назад", callback_data="teacher_menu")]
        ]
    )
    await callback.message.answer(
        "👩‍🏫 *Меню викладача*\n\n"
        "Оберіть дію, яку бажаєте виконати зі списку нижче 👇",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "add_lesson")
async def add_lesson(callback: CallbackQuery, state: FSMContext):
    """Починає процес створення заняття та запитує тему або скасування операції."""
    await callback.message.answer(
        "📝 *Введіть тему заняття:*\n"
        "Для скасувати — натисніть /cancel.",
        parse_mode="Markdown"
    )
    await state.set_state(LessonFactory.waiting_for_title)


@router.message(LessonFactory.waiting_for_title)
async def get_lesson_title(message: Message, state: FSMContext):
    """Обробляє назву заняття та пропонує вибір (календар або ручне введення)."""
    await state.update_data(title=message.text.strip())
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ввести дату вручну", callback_data="manual_date")],
            [InlineKeyboardButton(text="Вибрати дату через календар", callback_data="open_calendar")]
        ]
    )
    await message.answer(
        "📅 *Виберіть дату заняття за допомогою календаря:*\n"
        "✍️ *Або введіть дату вручну у форматі:* `РРРР.ММ.ДД`\n"
        "Для скасувати — натисніть /cancel.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await state.set_state(LessonFactory.waiting_for_date)


@router.callback_query(SimpleCalendarCallback.filter(), LessonFactory.waiting_for_date)
async def process_date_selection(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    """Обробляє вибір дати через inline-календар і запитує час заняття."""
    selected, date = await calendar.process_selection(callback, callback_data)
    if selected:
        await state.update_data(date=date)
        await callback.message.edit_text(
            f"✅ Дату обрано: {date.strftime('%d.%m.%Y')}\n"
            f"🕒 Тепер введіть час заняття (наприклад: 18:00):\n"
            "Для скасувати — натисніть /cancel."
        )
        await state.set_state(LessonFactory.waiting_for_time)


@router.callback_query(F.data == "manual_date", LessonFactory.waiting_for_date)
async def prompt_manual_date(callback: CallbackQuery, state: FSMContext):
    """Інформує користувача про формат ручного введення дати заняття."""
    await callback.message.answer(
        "✍️ Введіть дату вручну у форматі: `РРРР.ММ.ДД`\n"
        "_Наприклад:_ `2025.06.12`",
        parse_mode="Markdown"
    )
    await state.set_state(LessonFactory.waiting_for_manual_date)


@router.message(LessonFactory.waiting_for_manual_date)
async def handle_manual_date(message: Message, state: FSMContext):
    """Обробляє ручне введення дати у форматі РРРР.ММ.ДД та пропонує календар при помилці формату."""
    try:
        date = datetime.strptime(message.text.strip(), "%Y.%m.%d")

        current_year = datetime.now().year
        if not (current_year <= date.year <= current_year + 1):
            raise ValueError("Рік повинен бути поточним або наступним")

        await state.update_data(date=date)
        await message.answer(
            f"✅ Дата обрана: {date.strftime('%d.%m.%Y')}\n"
            f"🕒 Тепер введіть час заняття (наприклад: 18:00)\n"
            "❌ Для скасування натисніть /cancel."
        )
        await state.set_state(LessonFactory.waiting_for_time)
    except ValueError:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Скористуватися календарем", callback_data="open_calendar")]
            ]
        )
        await message.answer(
            "⚠ Невірний формат! Введіть дату у форматі: `2025.06.12`\n"
            "Або скористайтеся інлайн календарем, натиснувши кнопку нижче 👇",
            parse_mode="Markdown",
            reply_markup=keyboard
        )


@router.message(LessonFactory.waiting_for_time)
async def get_lesson_time(message: Message, state: FSMContext):
    """Процес створення заняття та запитує час заняття або скасування операції."""
    try:
        hour, minute = map(int, message.text.split(":"))
        if not (0 <= hour <= 24 and 0 <= minute <= 60):
            raise ValueError("Невірний формат")
        await state.update_data(hour=hour, minute=minute)

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🖥 Онлайн"), KeyboardButton(text="🏫 Офлайн")]
            ],
            resize_keyboard=True,
        )
        await message.answer(
            "📌 *Виберіть тип заняття:*\n"
            "Для скасувати — натисніть /cancel.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        await state.set_state(LessonFactory.waiting_for_type)
    except ValueError:
        await message.answer("⚠ Невірний формат! Введіть час у форматі ГГ:ХХ або /cancel для скасування.")


@router.message(LessonFactory.waiting_for_type)
async def get_lesson_type(message: Message, state: FSMContext):
    """Процес створення заняття Enam:з вибором типа заняття та запит введіть кількість місць або скасування операції."""
    type_text = message.text.strip().lower()
    if "онлайн" in type_text:
        lesson_type = LessonType.ONLINE
    elif "офлайн" in type_text:
        lesson_type = LessonType.OFFLINE
    else:
        await message.answer("⚠ Невірний вибір! Виберіть \n'🖥 Онлайн' або '🏫 Офлайн'.", )
        return

    await state.update_data(type_lesson=lesson_type)
    await message.answer(
        "👥  *Введіть кількість місць:*\n"
        "Для скасувати — натисніть /cancel.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove())

    await state.set_state(LessonFactory.waiting_for_places)


@router.message(LessonFactory.waiting_for_places)
async def get_lesson_places(message: Message, state: FSMContext):
    """Обробляє введення кількості місць для заняття та виводить підсумок з можливістю підтвердження,
     повторного заповнення або скасування."""
    try:
        places = int(message.text.strip())
        await state.update_data(places=places)

        lesson_data = await state.get_data()
        date = lesson_data.get('date')

        text_result = (
            f"Назва заняття:{lesson_data['title']}\n"
            f"Дата: {date.day:02d}.{date.month:02d}.{date.year}\n"
            f"Час: {lesson_data.get('hour', 0):02d}:{lesson_data.get('minute', 0):02d}\n"
            f"Тип: {'онлайн' if lesson_data.get('type_lesson') == LessonType.ONLINE else 'офлайн'}\n"
            f"Кількість місць: {lesson_data.get('places', 'не вказано')}"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="✅ Все вірно", callback_data="confirm_lesson")
            ], [
                InlineKeyboardButton(text="🔄 Заповнити знову", callback_data="add_lesson")
            ], [
                InlineKeyboardButton(text="❌ Скасувати", callback_data="lesson_creation_cancel")
            ]]
        )
        await message.answer(text_result, reply_markup=keyboard)
    except ValueError:
        await message.answer("⚠ Невірне значення! Введіть число або /cancel для скасування.")


@router.callback_query(F.data == "confirm_lesson")
async def confirm_lesson(callback: CallbackQuery, state: FSMContext):
    """Функція, яка заносить заняття до бази даних та повідомлює про успішне створення."""
    await callback.answer()  # уникаємо зависання
    lesson_data = await state.get_data()
    date = lesson_data.get('date')
    await callback.message.delete()

    await create_lesson(
        title=lesson_data["title"],
        year=date.year,
        month=date.month,
        day=date.day,
        hour=lesson_data["hour"],
        minute=lesson_data["minute"],
        type_lesson=lesson_data["type_lesson"],
        teacher_id_tg=callback.from_user.id,
        places=lesson_data["places"]
    )
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Повернутися до панелі вчителя", callback_data="teacher_menu")]
        ]
    )
    await callback.message.answer("✅ Заняття успішно створене!", reply_markup=keyboard)


@router.callback_query(F.data == "open_calendar",
                       StateFilter(LessonFactory.waiting_for_manual_date, LessonFactory.waiting_for_date))
async def open_calendar_handler(callback: CallbackQuery, state: FSMContext):
    """Відправляє інлайн-календар для вибору дати заняття."""
    keyboard = await open_calendar()
    await callback.message.edit_text(
        "📅 Оберіть дату через календар 👇",
        reply_markup=keyboard
    )
    await state.set_state(LessonFactory.waiting_for_date)


@router.callback_query(F.data == "lesson_creation_cancel")
async def cancel_lesson(callback: CallbackQuery, state: FSMContext):
    """Скасовує погодження заняття"""
    await callback.answer()  # уникаємо зависання
    await callback.message.delete()
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Повернутися до панелі вчителя", callback_data="teacher_menu")]
        ]
    )
    await callback.message.answer("❌ Створення заняття скасовано", reply_markup=keyboard)


@router.callback_query(F.data == "lessons_and_signups")
async def course_signups(callback: CallbackQuery):
    """Хендлер для викладачів, який виводить список запланованих занять на поточний та наступний тиждень
разом із переліком студентів, які записалися на кожне з них."""
    await callback.answer()
    await callback.message.delete()
    teacher, lessons = await show_teacher_lessons(callback)
    if not lessons:
        await callback.message.answer("ℹ️ На цей та наступний тиждень у вас немає запланованих занять.")
        return

    text_result = ""
    for i, lesson in enumerate(lessons, start=1):
        lesson_type = "🧑‍🏫 *Очно*" if lesson.type_lesson == LessonType.OFFLINE else "💻 *Онлайн*"
        lesson_datetime = lesson.datetime.strftime('%d.%m.%Y о %H:%M')
        lesson_places = f"{lesson.places} 🟦" if lesson.places >= 1 else "✅ Група повна "

        enrolled_users = lesson.enrollments
        enrolled_count = len(enrolled_users)
        total_places = lesson.places + enrolled_count

        user_list = "\n".join([
            f"{ent.full_name} : @{ent.user.login}" for ent in enrolled_users
        ]) or "—"

        text_result += (
            f"📚 *Заняття #{i}*\n"
            f"🏷️ *Тема:* `{lesson.title}`\n"
            f"📅 *Дата:* `{lesson_datetime}`\n"
            f"🏛️ *Формат:* {lesson_type}\n"
            f"🎫 *Вільних місць:* {lesson_places}\n"
            f"📌 *Всього місць:* {total_places}\n"
            f"👥 *Записалося:* {enrolled_count} студентів\n"
            f"📃 *Учні:*\n{user_list}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Видалити студента", callback_data="remove_student")],
            [InlineKeyboardButton(text="🔄 Оновити список", callback_data="lessons_and_signups")],
            [InlineKeyboardButton(text="⬅️ До меню викладача 👩‍🏫", callback_data="teachers")]
        ]
    )

    await callback.message.answer(text="📋 *Активні курси на цей та наступний тиждень:*\n\n" + text_result,
                                  parse_mode="Markdown",
                                  reply_markup=keyboard)


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


@router.callback_query(F.data == "remove_student")
async def remove_student(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вилучити з усіх занять", callback_data="remove_from_all_lessons")],
            [InlineKeyboardButton(text="Вилучити з певного заняття", callback_data="select_lesson_to_remove")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_teacher_menu")]
        ]
    )
    await callback.message.answer(text="📋 *Що ви хочете зробити зі студентом?*\n\n",
                                  parse_mode="Markdown",
                                  reply_markup=keyboard)


@router.callback_query(F.data == "remove_from_all_lessons")
async def remove_from_all_lessons(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    teacher, lessons = await show_teacher_lessons(callback)

    text_result = "🔻 Натисніть на кнопку з імʼям студента, щоб видалити його із заняття:\n"

    student_buttons = []
    unique_user_ids = set()
    unique_user_data = {}

    for lesson in lessons:
        for ent in lesson.enrollments:
            user_id = ent.user.id
            full_name = ent.full_name
            user_tg_id = ent.user_tg_id
            username = f"@{ent.user.login}"

            text_result += f"{full_name} :\n {username}\n"

            if user_id not in unique_user_ids:
                unique_user_ids.add(user_id)
                unique_user_data[user_id] = (username, user_tg_id)

    for user_id, (username, user_tg_id) in unique_user_data.items():
        student_buttons.append([
            InlineKeyboardButton(
                text=f"{username}",
                callback_data=f"remove_student:{user_tg_id}"
            )
        ])

    student_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="lessons_and_signups")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=student_buttons)

    await callback.message.answer(
        text=text_result,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("remove_student:"))
async def remove_student(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    student_tg_id = int(callback.data.split(":")[-1])

    teacher, lessons = await show_teacher_lessons(callback)

    button_menu = [[InlineKeyboardButton(text="🔙 Назад", callback_data="teachers")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=button_menu)

    for lesson in lessons:
        enrolled_users = lesson.enrollments
        for ent in enrolled_users:
            await remove_student_from_class(ent.lesson_id, student_tg_id)

    await callback.message.answer(
        text='✅ Користувача успішно видалено з усіх занять.',
        parse_mode="Markdown",
        reply_markup=keyboard
    )
