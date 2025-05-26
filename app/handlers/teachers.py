from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.keyboards.keyboards import back_button_builder, get_teachers_command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from app.database.admin_crud import get_enrollments_for_two_weeks,active_courses_for_two_weeks
from app.database.models import LessonType

router = Router()


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
            [InlineKeyboardButton(text="🔙 Повернутись назад", callback_data="admin_menu")]
        ]
    )
    await callback.message.answer(
        "👩‍🏫 *Меню викладача*\n\n"
        "Оберіть дію, яку бажаєте виконати зі списку нижче 👇",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "course_signups") #!!!
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


# @router.message(F.text == "Додати заняття")
# async def add_lesson(message: Message, state: FSMContext):
#     """Функція для додавання заняття"""
#     await message.answer("📝 Введіть тему заняття:\n\n🔹 Для скасування введіть /cancel")
#     await state.set_state(LessonFactory.waiting_for_title)



@router.callback_query(F.data == "active_courses")
async def course_signups(callback: CallbackQuery, state: FSMContext):
    lessons = await active_courses_for_two_weeks()
    if not lessons:
        await callback.message.answer("❌ Курсів на цей та наступний тиждень не знайдено.")
        return

    text_result = ""
    for i, lesson in enumerate(lessons, start=1):
        lesson_type = "🧑‍🏫 *Очно*" if lesson.type_lesson == LessonType.OFFLINE else "💻 *Онлайн*"
        lesson_places = f"{lesson.places} 🟦"if lesson.places >= 1 else "✅ Група повна "
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


