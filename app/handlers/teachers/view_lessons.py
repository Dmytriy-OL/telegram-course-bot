from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.core.models import LessonType
from app.handlers.utils import show_teacher_lessons
from app.keyboards.teachers import get_lesson_signups_keyboard

router = Router()


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

    await callback.message.answer(text="📋 *Активні курси на цей та наступний тиждень:*\n\n" + text_result,
                                  parse_mode="Markdown",
                                  reply_markup=get_lesson_signups_keyboard())
