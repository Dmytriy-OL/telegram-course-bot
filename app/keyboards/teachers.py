from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def teacher_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🆕 Додати заняття", callback_data="add_lesson")],
            [InlineKeyboardButton(text="📥 Заняття та записи", callback_data="lessons_and_signups")],
            [InlineKeyboardButton(text="✏️ Редагувати заняття", callback_data="edit_lessons")],
            [InlineKeyboardButton(text="🔗 Додати посилання на заняття", callback_data="lesson_link")],
            [InlineKeyboardButton(text="🔙 Повернутись назад", callback_data="teacher_menu")]
        ]
    )


def get_teachers_command():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍🏫 Для викладачів", callback_data="teachers")],
            [InlineKeyboardButton(text="👨🏻‍💻 Панель користувача", callback_data="go_to_main_menu")],
        ]
    )
    return keyboard


def confirm_lesson_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Все вірно", callback_data="confirm_lesson")],
            [InlineKeyboardButton(text="🔄 Заповнити знову", callback_data="add_lesson")],
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="lesson_creation_cancel")]
        ]
    )


def return_teacher_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Повернутися до панелі вчителя", callback_data="teacher_menu")]
        ]
    )


def remove_student_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вилучити з усіх занять", callback_data="remove_from_all_lessons")],
            [InlineKeyboardButton(text="Вилучити з певного заняття", callback_data="select_lesson_to_remove")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_teacher_menu")]
        ]
    )


def get_lesson_signups_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Видалити студента", callback_data="remove_student")],
            [InlineKeyboardButton(text="➕ Додати студента вручну", callback_data="add_student")],
            [InlineKeyboardButton(text="🔄 Оновити список", callback_data="lessons_and_signups")],
            [InlineKeyboardButton(text="⬅️ До меню викладача 👩‍🏫", callback_data="teachers")]
        ]
    )


def edit_single_lesson_menu(lesson_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Змінити тему", callback_data=f"edit_title:{lesson_id}")],
            [InlineKeyboardButton(text="📅 Змінити дату", callback_data=f"edit_date:{lesson_id}")],
            [InlineKeyboardButton(text="⏰ Змінити час", callback_data=f"edit_time:{lesson_id}")],
            [InlineKeyboardButton(text="👥 Змінити кількість місць", callback_data=f"edit_places:{lesson_id}")],
            [InlineKeyboardButton(text="🗑 Видалити заняття", callback_data=f"delete_lesson:{lesson_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="edit_lessons")]
        ]
    )


def add_student_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Повернутися до панелі вчителя", callback_data="teacher_menu")],
            [InlineKeyboardButton(text="🔄 Заповнити знову", callback_data="add_student")]

        ]
    )
