from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.database.crud.lessons import find_activities_by_date
from app.bot.keyboards.students import get_lesson_day_actions_keyboard, back_button_markup
from app.bot.keyboards.generators import generate_week_keyboard

router = Router()


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

            await callback.message.answer(lesson_text, parse_mode="Markdown",
                                          reply_markup=get_lesson_day_actions_keyboard(lesson.id, lesson.places))
    else:
        await callback.message.answer("❌ *Занять на цей день немає або їх ще не додали.*", parse_mode="Markdown",
                                      reply_markup=back_button_markup())


@router.callback_query(F.data == "select_this_week")
async def select_this_week(callback: CallbackQuery):
    """Відправляє клавіатуру для поточного тижня."""
    await callback.message.answer("📅 Оберіть день:", reply_markup=generate_week_keyboard())


@router.callback_query(F.data == "select_next_week")
async def select_next_week(callback: CallbackQuery):
    """Відправляє клавіатуру для наступного тижня."""
    await callback.message.answer("📅 Оберіть день:", reply_markup=generate_week_keyboard(offset=7))
