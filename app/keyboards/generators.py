from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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
