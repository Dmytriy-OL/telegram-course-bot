from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_booking_keyboard(record_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Скасувати запис", callback_data=f"cancel_confirmed_{record_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message")]
        ]
    )


def cancel_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Так", callback_data=f"cancel_lesson")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message")]
        ]
    )


def get_cancel_success_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data=f"go_to_main_menu")],
            [InlineKeyboardButton(text="🔄 Обновити записи", callback_data="my_bookings")]
        ]
    )


def get_successful_enrollment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Виконати ще один запис", callback_data="enroll_course")],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_to_main_menu")]
        ]
    )


def get_cancel_operation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Обрати інше заняття", callback_data="enroll_course")],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_to_main_menu")]
        ]
    )


def get_week_selection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔥 Записатися на цей тиждень 🔥", callback_data="select_this_week")],
            [InlineKeyboardButton(text="😃 Записатися на наступний тиждень 😃", callback_data="select_next_week")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message")]
        ]
    )


def get_lesson_day_actions_keyboard(lesson_id: int, places: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Записатися",
                callback_data=f"recording_day_{lesson_id}_{places}"
            )],
            [InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="remove_prev_message"
            )]
        ]
    )


def back_button_markup():
    """Функція для створення клавіатури з кнопкою 'Назад'."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="remove_prev_message")]]
    )


def get_student_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Записатися на курс 🔥", callback_data="enroll_course")],
        [InlineKeyboardButton(text="📜 Мої записи 📅", callback_data="my_bookings")],
        [InlineKeyboardButton(text="📲 Зв'язок із підтримкою 🤝", callback_data="support_contact")],
        [InlineKeyboardButton(text="🌍 Наш сайт 🔗", callback_data="visit_website")]
    ])
    return keyboard
