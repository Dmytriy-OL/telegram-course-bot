from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.handlers.utils import delete_lesson_messages
from app.database.crud.bot.lessons import edit_lesson, remove_lesson
from app.database.core.models import LessonType
from app.bot.keyboards.teachers import return_teacher_menu, teacher_main_menu, remove_lesson_by_id

router = Router()


class EditLesson(StatesGroup):
    waiting_for_edit_title = State()
    waiting_for_edit_date = State()
    waiting_for_edit_time = State()
    waiting_for_edit_places = State()
    waiting_for_edit_type = State()
    waiting_for_delete_lesson = State()


@router.callback_query(F.data.startswith("edit_title:"))
async def edit_title(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split(":")[1])

    await state.update_data(lesson_id=lesson_id)
    await callback.message.answer(
        "📝 *Введіть нову назву заняття:*\n"
        "Для скасувати — натисніть /cancel.",
        parse_mode="Markdown"
    )
    await state.set_state(EditLesson.waiting_for_edit_title)


@router.message(EditLesson.waiting_for_edit_title)
async def get_lesson_title(message: Message, state: FSMContext):
    title = message.text.strip()
    data = await state.get_data()
    lesson_id = data.get("lesson_id")

    if lesson_id is None:
        await message.answer("❗️Помилка: не вдалося знайти заняття для редагування.")
        await state.clear()
        return

    if title:
        await edit_lesson(lesson_id, title=title)
        await message.answer("✅ Назву заняття змінено.",
                             parse_mode="Markdown",
                             reply_markup=return_teacher_menu())
    else:
        await message.answer("❗️Будь ласка, введіть коректну назву заняття.",
                             parse_mode="Markdown",
                             reply_markup=return_teacher_menu())
    await state.clear()


@router.callback_query(F.data.startswith("edit_date:"))
async def edit_date(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split(":")[1])
    await state.update_data(lesson_id=lesson_id)
    await callback.message.answer(
        "✍️ Введіть нову дату вручну у форматі: `РРРР.ММ.ДД`\n"
        "_Наприклад:_ `2025.06.12`",
        parse_mode="Markdown"
    )
    await state.set_state(EditLesson.waiting_for_edit_date)


@router.message(EditLesson.waiting_for_edit_date)
async def get_edit_date(message: Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text.strip(), "%Y.%m.%d")
        current_year = datetime.now().year

        data = await state.get_data()
        lesson_id = data.get("lesson_id")

        if lesson_id is None:
            await message.answer("❗️Помилка: не вдалося знайти заняття для редагування.")
            await state.clear()
            return

        valid_year = current_year <= date.year <= current_year + 1
        if not valid_year:
            raise ValueError("Рік повинен бути поточним або наступним")

        await edit_lesson(lesson_id, new_date=date)
        await message.answer(
            f"✅ Дата зміняна: {date.strftime('%d.%m.%Y')}",
            parse_mode="Markdown",
            reply_markup=return_teacher_menu())
        await state.clear()

    except ValueError:
        await message.answer("❗️Будь ласка, введіть коректну дату заняття.",
                             parse_mode="Markdown",
                             reply_markup=return_teacher_menu())


@router.callback_query(F.data.startswith("edit_time:"))
async def edit_time(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split(":")[1])

    await state.update_data(lesson_id=lesson_id)
    await callback.message.answer(
        "🕒 *Введіть новий час заняття (наприклад: 18:00):*\n"
        "Для скасувати — натисніть /cancel.",
        parse_mode="Markdown"
    )
    await state.set_state(EditLesson.waiting_for_edit_time)


@router.message(EditLesson.waiting_for_edit_time)
async def get_edit_time(message: Message, state: FSMContext):
    try:
        new_time = datetime.strptime(message.text.strip(), "%H:%M").time()

        data = await state.get_data()
        lesson_id = data.get("lesson_id")

        if lesson_id is None:
            await message.answer("❗️Помилка: не вдалося знайти заняття для редагування.")
            await state.clear()
            return

        await edit_lesson(lesson_id, new_time=new_time)
        await message.answer(
            f"🕒 Час змінено на : {new_time.strftime('%H:%M')}",
            parse_mode="Markdown",
            reply_markup=return_teacher_menu())
        await state.clear()

    except ValueError:
        await message.answer("❗️Будь ласка, введіть коректний час.",
                             parse_mode="Markdown",
                             reply_markup=return_teacher_menu())


@router.callback_query(F.data.startswith("edit_places:"))
async def edit_places(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split(":")[1])

    await state.update_data(lesson_id=lesson_id)
    await callback.message.answer(
        "👥  *Введіть кількість місць:*\n"
        "Для скасувати — натисніть /cancel.",
        parse_mode="Markdown"
    )
    await state.set_state(EditLesson.waiting_for_edit_places)


@router.message(EditLesson.waiting_for_edit_places)
async def get_edit_places(message: Message, state: FSMContext):
    try:
        places = int(message.text.strip())

        if places <= 0:
            raise ValueError("Кількість місць має бути більше нуля")

        data = await state.get_data()
        lesson_id = data.get("lesson_id")

        if lesson_id is None:
            await message.answer("❗️Помилка: не вдалося знайти заняття для редагування.")
            await state.clear()
            return

        await edit_lesson(lesson_id, places=places)
        await message.answer(
            f"✅ Кількість студентів зміннено : {places}",
            parse_mode="Markdown",
            reply_markup=return_teacher_menu())
        await state.clear()

    except ValueError:
        await message.answer("❗️Будь ласка, введіть коректну кількість місць (додатне число).",
                             parse_mode="Markdown",
                             reply_markup=return_teacher_menu())


@router.callback_query(F.data.startswith("edit_type:"))
async def edit_type(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split(":")[1])

    await state.update_data(lesson_id=lesson_id)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🖥 Онлайн"), KeyboardButton(text="🏫 Офлайн")]
        ],
        resize_keyboard=True,
    )
    await callback.message.answer(
        "📌 *Виберіть тип заняття:*\n"
        "Для скасувати — натисніть /cancel.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await state.set_state(EditLesson.waiting_for_edit_type)


@router.message(EditLesson.waiting_for_edit_type)
async def get_edit_type(message: Message, state: FSMContext):
    try:
        type_text = message.text.strip().lower()
        if "онлайн" in type_text:
            lesson_type = LessonType.ONLINE
        elif "офлайн" in type_text:
            lesson_type = LessonType.OFFLINE
        else:
            await message.answer("⚠ Невірний вибір! Виберіть \n'🖥 Онлайн' або '🏫 Офлайн'.", )
            return

        data = await state.get_data()
        lesson_id = data.get("lesson_id")

        if lesson_id is None:
            await message.answer("❗️Помилка: не вдалося знайти заняття для редагування.")
            await state.clear()
            return

        await edit_lesson(lesson_id, type_lesson=lesson_type)

        display_type = "🖥 Онлайн" if lesson_type == LessonType.ONLINE else "🏫 Офлайн"
        await message.answer(
            f"✅ Тип заняття змінено: {display_type}",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            "📋 Оберіть наступну дію:",
            reply_markup=return_teacher_menu()
        )
        await state.clear()

    except ValueError:
        await message.answer("❗️Будь ласка, введіть коректну кількість місць (додатне число).",
                             parse_mode="Markdown",
                             reply_markup=return_teacher_menu())


@router.callback_query(F.data.startswith("remove_lesson:"))
async def edit_remove_lesson(callback: CallbackQuery):
    lesson_id = int(callback.data.split(":")[1])
    await callback.message.answer(
        "📌 *Ви впевнені,що хочете видалити заняття:*\n",
        parse_mode="Markdown",
        reply_markup=remove_lesson_by_id(lesson_id)
    )


@router.callback_query(F.data.startswith("delete_lesson:"))
async def delete_lesson(callback: CallbackQuery):
    lesson_id = int(callback.data.split(":")[1])
    deleted = await remove_lesson(lesson_id)
    if deleted:
        await callback.message.answer(
            "✅ Заняття вдало видалено",
            parse_mode="Markdown",
            reply_markup=return_teacher_menu()
        )
    else:
        await callback.message.answer(
            "❗️Це заняття вже було видалене або не існує.",
            parse_mode="Markdown",
            reply_markup=return_teacher_menu()
        )


@router.callback_query(F.data == "delete_lesson_messages")
async def handle_delete_lesson_messages(callback: CallbackQuery, state: FSMContext):
    """Видаляє список повідомлень"""
    await delete_lesson_messages(callback, state)


@router.callback_query(F.data == "teacher_menu_clean")
async def teacher_back_and_delete(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await delete_lesson_messages(callback, state)

    await callback.message.answer(
        "📋 Меню викладача:",
        reply_markup=teacher_main_menu()
    )
