from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from app.bot.handlers.utils import show_teacher_lessons
from app.bot.keyboards.teachers import return_teacher_menu, add_student_menu_keyboard
from app.database.crud.bot.lessons import enroll_student_to_lesson

router = Router()


class LessonFactory(StatesGroup):
    waiting_for_title_lesson = State()
    waiting_for_full_name = State()


@router.callback_query(F.data == "add_student")
async def add_student(callback: CallbackQuery, state: FSMContext):
    teacher, lessons = await show_teacher_lessons(callback)

    if lessons:
        await state.update_data(teacher=teacher, lessons=lessons)
        await callback.message.answer(
            "📝 *Введіть назву заняття:*\n"
            "Для скасувати — натисніть /cancel.",
            parse_mode="Markdown"
        )
        await state.set_state(LessonFactory.waiting_for_title_lesson)
    else:
        await callback.message.answer("⚠️ У вас поки що немає занять.",
                                      parse_mode="Markdown",
                                      reply_markup=return_teacher_menu())


@router.message(LessonFactory.waiting_for_title_lesson)
async def get_lesson_title(message: Message, state: FSMContext):
    data = await state.get_data()
    lessons: list = data.get("lessons", [])
    title = message.text.strip()

    matched_lesson = next((lesson for lesson in lessons if lesson.title == title), None)

    if matched_lesson:
        if matched_lesson.places > 0:
            await state.update_data(selected_lesson_id=matched_lesson.id)
            await message.answer(
                "📝 *Напишіть прізвище та ім'я студента:*\n"
                "_Наприклад: Олійник Дмитрій_",
                parse_mode="Markdown"
            )
            await state.set_state(LessonFactory.waiting_for_full_name)
        else:
            await state.clear()
            await message.answer(
                "⚠️ У цьому занятті більше немає вільних місць.",
                parse_mode="Markdown",
                reply_markup=add_student_menu_keyboard()
            )
    else:
        await state.clear()
        await message.answer(
            "❌ Неправильна назва заняття. Спробуйте ще раз або натисніть /cancel.",
            parse_mode="Markdown",
            reply_markup=add_student_menu_keyboard()
        )


@router.message(LessonFactory.waiting_for_full_name)
async def get_student_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    if len(full_name.split()) >= 2:
        data = await state.get_data()
        lesson_id = data.get("selected_lesson_id")

        await enroll_student_to_lesson(lesson_id, message.from_user.id, full_name)
        await message.answer(
            f"✅ {full_name}, ви успішно записали на заняття!",
            parse_mode="Markdown",
            reply_markup=return_teacher_menu()
        )
        await state.clear()
    else:
        await state.clear()
        await message.answer(
            "❌ Неправильно ввели прізвище та ім'я студента. Спробуйте ще раз або натисніть /cancel.",
            parse_mode="Markdown",
            reply_markup=add_student_menu_keyboard()
        )
