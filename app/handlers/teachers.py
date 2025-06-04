from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.keyboards.keyboards import back_button_builder, get_teachers_command
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from app.database.admin_crud import get_enrollments_for_two_weeks, active_courses_for_two_weeks
from app.database.crud import create_lesson, set_user
from app.database.models import LessonType
from app.handlers.utils import delete_previous_message
router = Router()


class LessonFactory(StatesGroup):
    waiting_for_title = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_type = State()
    waiting_for_places = State()


@router.callback_query(F.data == "teachers")
async def teachers(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🆕 Додати заняття", callback_data="add_lesson")],
            [InlineKeyboardButton(text="📥 Записи на курси", callback_data="course_signups")],
            [InlineKeyboardButton(text="📚 Активні курси", callback_data="active_courses")],
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
    if callback.message.text.strip().casefold() == "/cancel":
        await state.clear()
        await callback.message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    await callback.message.answer("Введіть тему заннятя:")
    await state.set_state(LessonFactory.waiting_for_title)


@router.message(LessonFactory.waiting_for_title)
async def get_lesson_title(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    await state.update_data(title=message.text.strip())
    await message.answer("📅 Введіть дату заняття у форматі РРРР-ММ-ДД:")
    await state.set_state(LessonFactory.waiting_for_date)


@router.message(LessonFactory.waiting_for_date)
async def get_lesson_date(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    try:
        year, month, day = map(int, message.text.split("-"))
        await state.update_data(year=year, month=month, day=day)
        await message.answer("⏰ Введіть час заняття у форматі ГГ:ХХ:")
        await state.set_state(LessonFactory.waiting_for_time)
    except ValueError:
        await message.answer("⚠ Невірний формат! Введіть дату у форматі РРРР-ММ-ДД або /cancel для скасування.")


@router.message(LessonFactory.waiting_for_time)
async def get_lesson_time(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    try:
        hour, minute = map(int, message.text.split(":"))
        await state.update_data(hour=hour, minute=minute)

        # Вибір типу заняття
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🖥 Онлайн"), KeyboardButton(text="🏫 Офлайн")]
            ],
            resize_keyboard=True,
        )
        await message.answer("📌 Виберіть тип заняття:", reply_markup=keyboard)
        await state.set_state(LessonFactory.waiting_for_type)
    except ValueError:
        await message.answer("⚠ Невірний формат! Введіть час у форматі ГГ:ХХ або /cancel для скасування.")


@router.message(LessonFactory.waiting_for_type)
async def get_lesson_type(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    type_text = message.text.strip().lower()
    if "онлайн" in type_text:
        lesson_type = LessonType.ONLINE
    elif "офлайн" in type_text:
        lesson_type = LessonType.OFFLINE
    else:
        await message.answer("⚠ Невірний вибір! Виберіть '🖥 Онлайн' або '🏫 Офлайн'.")
        return

    await state.update_data(type_lesson=lesson_type)
    await message.answer("👥 Введіть кількість місць:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(LessonFactory.waiting_for_places)


@router.message(LessonFactory.waiting_for_places)
async def get_lesson_places(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    try:
        places = int(message.text.strip())
        await state.update_data(places=places)

        lesson_data = await state.get_data()

        text_result = (
            f"Назва заняття: {lesson_data['title']}\n"
            f"Дата: {lesson_data['day']:02d}.{lesson_data['month']:02d}.{lesson_data['year']}\n"
            f"Час: {lesson_data['hour']:02d}:{lesson_data['minute']:02d}\n"
            f"Тип: {'онлайн' if lesson_data['type_lesson'] == LessonType.ONLINE else 'офлайн'}\n"
            f"Кількість місць: {lesson_data['places']}"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="✅ Все вірно", callback_data="confirm_lesson")
            ], [
                InlineKeyboardButton(text="🔄 Заповнити знову", callback_data="retry_lesson")
            ], [
                InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_lesson")
            ]]
        )
        await message.answer(text_result, reply_markup=keyboard)
    except ValueError:
        await message.answer("⚠ Невірне значення! Введіть число або /cancel для скасування.")


@router.callback_query(F.data == "confirm_lesson")
async def confirm_lesson(callback: CallbackQuery, state: FSMContext):
    """Функція, яка заносить заняття до бази даних та повідомлює про успішне створення."""
    lesson_data = await state.get_data()
    await callback.message.delete()

    await create_lesson(
        title=lesson_data["title"],
        year=lesson_data["year"],
        month=lesson_data["month"],
        day=lesson_data["day"],
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


@router.callback_query(F.data == "course_signups")  # !!!
async def course_signups(callback: CallbackQuery, state: FSMContext):
    """Переглядаємо записи учнів на заняття"""
    enrollments = await get_enrollments_for_two_weeks()
    if not enrollments:
        await callback.message.answer("❌ Записів учнів за цей та наступний тиждень не знайдено.")
        return

    text_result = ""
    for i, enrollment in enumerate(enrollments, start=1):
        lesson = enrollment.lesson
        user = enrollment.user
        lesson_type = "🧑‍🏫 *Очно*" if lesson.type_lesson == LessonType.OFFLINE else "💻 *Онлайн*"
        text_result += (
            f"*Учень #{i}*\n"
            f"*Назва заняття:* `{lesson.title}`\n"
            f"*Телеграм:* `{user.login}`\n"
            f"*Ім’я та прізвище:* `{user.name or 'Невідомо'} {user.surname or ''}`\n"
            f"*Дата та час:* `{lesson.datetime.strftime('%d.%m.%Y %H:%M')}`\n"
            f"*Формат:* {lesson_type}\n"
            f"*Викладач:* `{lesson.instructor}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    await callback.message.answer(text="📋 *Записи учнів на цей та наступний тиждень:*\n\n" + text_result,
                                  parse_mode="Markdown",
                                  reply_markup=back_button_builder().as_markup())


@router.callback_query(F.data == "active_courses")
async def course_signups(callback: CallbackQuery, state: FSMContext):
    lessons = await active_courses_for_two_weeks()
    if not lessons:
        await callback.message.answer("❌ Курсів на цей та наступний тиждень не знайдено.")
        return

    text_result = ""
    for i, lesson in enumerate(lessons, start=1):
        lesson_type = "🧑‍🏫 *Очно*" if lesson.type_lesson == LessonType.OFFLINE else "💻 *Онлайн*"
        lesson_places = f"{lesson.places} 🟦" if lesson.places >= 1 else "✅ Група повна "
        text_result += (
            f"*Заняття #{i}*\n"
            f"*Назва заняття:* `{lesson.title}`\n"
            f"*Викладач:* `{lesson.instructor}`\n"
            f"*Кількість місць:* `{lesson_places}`\n"
            f"*Дата та час:* `{lesson.datetime.strftime('%d.%m.%Y %H:%M')}`\n"
            f"*Формат:* {lesson_type}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    await callback.message.answer(text="📋 *Активні курси на цей та наступний тиждень:*\n\n" + text_result,
                                  parse_mode="Markdown",
                                  reply_markup=back_button_builder().as_markup())


@router.callback_query(F.data == "teacher_menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        text="Оберіть дію з меню адміністратора:",
        reply_markup=get_teachers_command()
    )
