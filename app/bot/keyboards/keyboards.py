from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)


def back_button_builder(text: str = '🔙 Назад') -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=text, callback_data="remove_prev_message"))
    return keyboard


def get_admin_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛡️ Адміни", callback_data="admin_admins")],
            [InlineKeyboardButton(text="👨🏻‍💻‍ Викладачі", callback_data="add_teacher")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📝 Зміни головного текст", callback_data="edit_main_text")],
            [InlineKeyboardButton(text="🖼️ Зміни зображення", callback_data="edit_main_image")],
            [InlineKeyboardButton(text="👨‍🏫 Для викладачів", callback_data="teachers")],
            [InlineKeyboardButton(text="👨🏻‍💻 Панель користувача", callback_data="go_to_main_menu")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="pass")],

        ]
    )
    return keyboard
