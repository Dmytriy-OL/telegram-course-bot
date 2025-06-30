from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.core.models import LessonType, Lesson
from app.handlers.utils import show_teacher_lessons
from app.keyboards.teachers import get_lesson_signups_keyboard, edit_single_lesson_menu

router = Router()


@router.callback_query(F.data.startswith("lessons_and_signups:view"))
async def course_signups(callback: CallbackQuery):
    """Хендлер для викладачів, який виводить список запланованих занять на поточний та наступний тиждень
разом із переліком студентів, які записалися на кожне з них."""
    await callback.answer()
    await callback.message.delete()

    mode = callback.data.split(":")[-1]
    mode = "view" if mode == "view" else "edit"
    teacher, lessons = await show_teacher_lessons(callback)
    if not lessons:
        await callback.message.answer("ℹ️ На цей та наступний тиждень у вас немає запланованих занять.")
        return

    text_result = ""
    for i, lesson in enumerate(lessons, start=1):
        text_result += format_lesson_text(i, lesson, mode)

    if mode == "view":
        keyboard = get_lesson_signups_keyboard()
    else:
        keyboard = edit_single_lesson_menu()

    await callback.message.answer(text="📋 *Активні курси на цей та наступний тиждень:*\n\n" + text_result,
                                  parse_mode="Markdown",
                                  reply_markup=keyboard)


def format_lesson_text(i: int, lesson: Lesson, mode: str = "view") -> str:
    lesson_type = "🧑‍🏫 *Очно*" if lesson.type_lesson == LessonType.OFFLINE else "💻 *Онлайн*"
    lesson_datetime = lesson.datetime.strftime('%d.%m.%Y о %H:%M')
    lesson_places = f"{lesson.places} 🟦" if lesson.places >= 1 else "✅ Група повна "
    enrolled_users = lesson.enrollments
    enrolled_count = len(enrolled_users)
    total_places = lesson.places + enrolled_count
    user_list = "\n".join([
        f"{ent.full_name} : @{ent.user.login}" for ent in enrolled_users
    ]) or "—"

    text = (
        f"📚 *Заняття #{i}*\n"
        f"🏷️ *Тема:* `{lesson.title}`\n"
        f"📅 *Дата:* `{lesson_datetime}`\n"
        f"🏛️ *Формат:* {lesson_type}\n"
        f"🎫 *Вільних місць:* {lesson_places}\n"
        f"📌 *Всього місць:* {total_places}\n"
        f"👥 *Записалося:* {enrolled_count} студентів\n"
    )

    if mode == "view":
        text += f"📃 *Учні:*\n{user_list}\n"

    return text + "━━━━━━━━━━━━━━━━━━━━━━\n"
