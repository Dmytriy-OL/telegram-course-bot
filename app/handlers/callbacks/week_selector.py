from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import datetime, timedelta
from app.database.crud import find_activities_by_date
from app.keyboards.keyboards import back_button_markup

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


@router.callback_query(F.data == "select_this_week")
async def select_this_week(callback: CallbackQuery):
    """Відправляє клавіатуру для поточного тижня."""
    await callback.message.answer("📅 Оберіть день:", reply_markup=generate_week_keyboard())


@router.callback_query(F.data == "select_next_week")
async def select_next_week(callback: CallbackQuery):
    """Відправляє клавіатуру для наступного тижня."""
    await callback.message.answer("📅 Оберіть день:", reply_markup=generate_week_keyboard(offset=7))
