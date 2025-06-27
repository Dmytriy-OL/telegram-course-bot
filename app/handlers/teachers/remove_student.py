from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from app.database.crud.lessons import remove_enrollment_for_student
from app.handlers.utils import show_teacher_lessons, delete_lesson_messages
from app.keyboards.teachers import remove_student_menu

router = Router()


@router.callback_query(F.data == "remove_student")
async def remove_student(callback: CallbackQuery):
    await callback.message.answer(text="📋 *Що ви хочете зробити зі студентом?*\n\n",
                                  parse_mode="Markdown",
                                  reply_markup=remove_student_menu())


@router.callback_query(F.data == "remove_from_all_lessons")
async def remove_from_all_lessons(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    teacher, lessons = await show_teacher_lessons(callback)

    text_result = "🔻 Натисніть на кнопку з імʼям студента, щоб видалити його із заняття:\n"

    student_buttons = []
    unique_user_ids = set()
    unique_user_data = {}

    for lesson in lessons:
        for ent in lesson.enrollments:
            user_id = ent.user.id
            full_name = ent.full_name
            user_tg_id = ent.user_tg_id
            username = f"@{ent.user.login}"

            text_result += f"{full_name} :\n {username}\n"

            if user_id not in unique_user_ids:
                unique_user_ids.add(user_id)
                unique_user_data[user_id] = (username, user_tg_id)

    for user_id, (username, user_tg_id) in unique_user_data.items():
        student_buttons.append([
            InlineKeyboardButton(
                text=f"{username}",
                callback_data=f"remove_student:{user_tg_id}"
            )
        ])

    student_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="lessons_and_signups")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=student_buttons)

    await callback.message.answer(
        text=text_result,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("remove_student:"))
async def remove_student(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    student_tg_id = int(callback.data.split(":")[-1])

    if student_tg_id > 1000:
        student_id = student_tg_id
        student_record = None
        text_result = '✅ Користувача успішно видалено з усіх занять.'
    else:
        student_id = None
        student_record = student_tg_id
        text_result = "✅ Користувача успішно видалено з заняття."

    teacher, lessons = await show_teacher_lessons(callback)

    button_menu = [[InlineKeyboardButton(text="🔙 Назад", callback_data="teachers")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=button_menu)

    for lesson in lessons:
        await remove_enrollment_for_student(
            lessons_id=lesson.id,
            student_id=student_id,
            student_record=student_record
        )
    await callback.message.answer(
        text=text_result,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "select_lesson_to_remove")
async def remove_from_lesson(callback: CallbackQuery, state: FSMContext):
    teacher, lessons = await show_teacher_lessons(callback)

    message_ids = []

    for lesson in lessons:
        text_result = (
            "🔻 *Натисніть на кнопку з імʼям студента, щоб видалити його із заняття:*\n\n"
            f"📚 *Заняття:* {lesson.title}\n\n👥 *Учні:*\n"
        )
        student_buttons = []

        for ent in lesson.enrollments:
            full_name = ent.full_name
            username = f"@{ent.user.login}" if ent.user.login else "Немає username"

            text_result += f"▫️ {full_name}\n({username})\n"
            student_buttons.append([
                InlineKeyboardButton(
                    text=full_name,
                    callback_data=f"remove_student:{ent.id}"
                )
            ])
        text_result += (
            "\n❗️_Натиснувши кнопку «Назад», усі ці повідомлення буде видалено._"
        )

        student_buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="delete_lesson_messages")
        ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=student_buttons)

        msg = await callback.message.answer(
            text=text_result,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        message_ids.append(msg.message_id)

    await state.update_data(lesson_message_ids=message_ids)


@router.callback_query(F.data == "delete_lesson_messages")
async def handle_delete_lesson_messages(callback: CallbackQuery, state: FSMContext):
    """Видаляє список повідомлень"""
    await delete_lesson_messages(callback, state)
