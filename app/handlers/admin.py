from aiogram.filters import Command, StateFilter
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.database.crud import delete_image_from_db, view_user, create_lesson
from app.handlers.utils import display_images
from app.database.models import Lesson, LessonType
from app.database.admin_crud import view_admins, view_users, add_caption, get_all_captions, main_captions_switch, \
    delete_captions, view_image, main_image_switch, get_enrollments_for_two_weeks,active_courses_for_two_weeks
from app.keyboards.keyboards import back_button_builder, get_admin_command
from app.handlers.callbacks import delete_previous_message
from app.database.upload_image import save_image_to_disk_and_db, delete_image_to_disk_and_db
from app.images import BASE_DIR

router = Router()


class DeleteImageState(StatesGroup):
    waiting_for_filename = State()


class CancelOperation(StatesGroup):
    cancel_operation = State()


class NewEntry(StatesGroup):
    waiting_for_title = State()
    waiting_for_caption = State()
    waiting_for_main_text_title = State()
    waiting_for_header_removal = State()


class ImageProcessor(StatesGroup):
    waiting_for_image = State()
    waiting_for_title_image = State()
    waiting_for_delete_image = State()
    waiting_for_main_title = State()


# class WorkWithRecords(StatesGroup):
#     waiting_for_main_text_title = State()
class LessonFactory(StatesGroup):
    waiting_for_title = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_type = State()
    waiting_for_places = State()


@router.callback_query(F.data == "edit_main_text")
async def edit_main_text_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Додати новий текст", callback_data="add_new_text")],
            [InlineKeyboardButton(text="📄 Переглянути всі тексти", callback_data="view_all_texts")],
            [InlineKeyboardButton(text="⭐ Вибрати головний текст", callback_data="select_main_text")],
            [InlineKeyboardButton(text="🗑️ Видалити текст", callback_data="delete_text")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")]
        ]
    )

    await callback.message.answer("🔧 *Оберіть дію над текстами:*", parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "edit_main_image")
async def edit_main_image_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖼️ Додати нове зображення", callback_data="add_new_image")],
            [InlineKeyboardButton(text="📚 Переглянути всі зображення", callback_data="view_all_image")],
            [InlineKeyboardButton(text="🌟 Вибрати головне зображення", callback_data="select_main_image")],
            [InlineKeyboardButton(text="🗑️ Видалити зображення", callback_data="delete_image")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")]
        ]
    )

    await callback.message.answer("🎨 *Що робимо з картинками?* Обери варіант нижче 👇", parse_mode="Markdown",
                                  reply_markup=keyboard)


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Кількість користувачів:", callback_data="total_stats_user")],
            [InlineKeyboardButton(text="⚠️ Незавершені записи користувачів:", callback_data="incomplete_signups")],
            [InlineKeyboardButton(text="📈 Інформацію про користувачів:", callback_data="user_count")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")]
        ]
    )

    await callback.message.answer("📊 *Які дії будем переглядати?* Обери варіант нижче 👇", parse_mode="Markdown",
                                  reply_markup=keyboard)


@router.callback_query(F.data == "teachers")
async def teachers(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🆕 Додати заняття", callback_data="add_lesson")],
            [InlineKeyboardButton(text="📥 Записи на курси", callback_data="course_signups")],
            [InlineKeyboardButton(text="📚 Активні курси", callback_data="active_courses")],
            [InlineKeyboardButton(text="✏️ Редагувати заняття", callback_data="edit_lessons")],
            [InlineKeyboardButton(text="🔗 Додати посилання на заняття", callback_data="lesson_link")],
            [InlineKeyboardButton(text="🔙 Повернутись назад", callback_data="admin_menu")]
        ]
    )

    await callback.message.answer(
        "👩‍🏫 *Меню викладача*\n\n"
        "Оберіть дію, яку бажаєте виконати зі списку нижче 👇",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "course_signups")
async def course_signups(callback: CallbackQuery, state: FSMContext):
    enrollments = await get_enrollments_for_two_weeks()
    if not enrollments:
        await callback.message.answer("❌ Записів учнів за цей та наступний тиждень не знайдено.")
        return

    text_result = ""
    for i, enrollment in enumerate(enrollments, start=1):
        lesson = enrollment.lesson
        user = enrollment.user
        lesson_type = "🧑‍🏫 *Очно*" if lesson.type_lesson == LessonType.OFFLINE else "💻 *Онлайн*"
        text_result += (
            f"*Учень #{i}*\n"
            f"*Назва заняття:* `{lesson.title}`\n"
            f"*Телеграм:* `{user.login}`\n"
            f"*Ім’я та прізвище:* `{user.name or 'Невідомо'} {user.surname or ''}`\n"
            f"*Дата та час:* `{lesson.datetime.strftime('%d.%m.%Y %H:%M')}`\n"
            f"*Формат:* {lesson_type}\n"
            f"*Викладач:* `{lesson.instructor}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    await callback.message.answer(text="📋 *Записи учнів на цей та наступний тиждень:*\n\n" + text_result,
                                  parse_mode="Markdown",
                                  reply_markup=back_button_builder().as_markup())


@router.callback_query(F.data == "active_courses")
async def course_signups(callback: CallbackQuery, state: FSMContext):
    lessons = await active_courses_for_two_weeks()
    if not lessons:
        await callback.message.answer("❌ Курсів на цей та наступний тиждень не знайдено.")
        return

    text_result = ""
    for i, lesson in enumerate(lessons, start=1):
        lesson_type = "🧑‍🏫 *Очно*" if lesson.type_lesson == LessonType.OFFLINE else "💻 *Онлайн*"
        lesson_places = f"{lesson.places} 🟦"if lesson.places >= 1 else "✅ Група повна "
        text_result += (
            f"*Заняття #{i}*\n"
            f"*Назва заняття:* `{lesson.title}`\n"
            f"*Викладач:* `{lesson.instructor}`\n"
            f"*Кількість місць:* `{lesson_places}`\n"
            f"*Дата та час:* `{lesson.datetime.strftime('%d.%m.%Y %H:%M')}`\n"
            f"*Формат:* {lesson_type}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    await callback.message.answer(text="📋 *Активні курси на цей та наступний тиждень:*\n\n" + text_result,
                                  parse_mode="Markdown",
                                  reply_markup=back_button_builder().as_markup())


@router.callback_query(F.data == "select_main_image")
async def select_main_image(callback: CallbackQuery, state: FSMContext):
    images = await view_image()
    if not images:
        await callback.message.answer("❌ Зображень не знайдено.")
        return
    text_result = ""
    for i, image in enumerate(images, start=1):
        text_result += (
            f"📄 *Зображення #{i}*\n"
            f"🔖 *Назва зображення:* `{image.filename}`\n"
            f"{'⭐️ ГОЛОВНЕ ЗОБРАЖЕННЯ ⭐️' if image.main_image else '▪️Не головне'}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )
    await callback.message.answer(text="🗂 *Ось усі назви зображень::*\n\n" + text_result, parse_mode="Markdown")
    text = (
        "📋  *Введіть назву малюнка, якого хочете зробити головним:*\n\n"
        f"🔹 Для скасування натисніть /cancel"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await state.set_state(ImageProcessor.waiting_for_main_title)


@router.message(ImageProcessor.waiting_for_main_title)
async def process_main_image_title(message: Message, state: FSMContext):
    title = message.text.strip()

    if title == "/cancel":
        # Якщо скасування, очищаємо стан
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
        return

    # Викликаємо функцію для зміни головного тексту
    main_image = await main_image_switch(title)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_text")],
            [InlineKeyboardButton(text="🔄 Ввести заголовок ще раз:", callback_data="select_main_image")],
        ])

    # Виводимо повідомлення користувачу
    if main_image:
        await message.answer(main_image, reply_markup=keyboard)

    # Очищаємо стан після виконання операції
    await state.clear()


@router.callback_query(F.data == "delete_image")
async def delete_image(callback: CallbackQuery, state: FSMContext):
    images = await view_image()
    if not images:
        await callback.message.answer("❌ Зображень не знайдено.")
        return
    await state.update_data(images=images)
    text_result = ""
    for i, image in enumerate(images, start=1):
        text_result += (
            f"📄 *Зображення #{i}*\n"
            f"🔖 *Назва зображення:* `{image.filename}`\n"
            f"{'⭐️ ГОЛОВНЕ ЗОБРАЖЕННЯ ⭐️' if image.main_image else '▪️Не головне'}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_image")],
            [InlineKeyboardButton(text="🗑️ Видалити зображення:", callback_data="filename_delete")],
        ])
    await callback.message.answer(text="🗂 *Ось усі назви зображень::*\n\n" + text_result, parse_mode="Markdown",
                                  reply_markup=keyboard)


@router.callback_query(F.data == "filename_delete")
async def filename_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введіть назву зображення, яке хочете видалити 🗑️️")
    await state.set_state(ImageProcessor.waiting_for_delete_image)


@router.message(ImageProcessor.waiting_for_delete_image)
async def delete_image_title(message: Message, state: FSMContext):
    title = message.text.strip()
    data = await state.get_data()
    images = data.get("images")

    for image in images:
        if title == image.filename:
            await delete_image_to_disk_and_db(title)
            await state.clear()
            await message.answer("✅ Зображення вдало видалено 🗑️", reply_markup=get_admin_command())
            return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_text")],
            [InlineKeyboardButton(text="🔄 Ввести заголовок ще раз:", callback_data="filename_delete")],
        ])
    await message.answer(f"❌ Зображення `{title}` не знайдено.", parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "view_all_image")
async def view_all_image(callback: CallbackQuery):
    images = await view_image()

    if not images:
        await callback.message.answer("❌ Зображень не знайдено.")
        return

    for image in images:
        image_path = BASE_DIR / f"{image.filename}.jpg"

        if image_path.exists():
            await callback.message.answer_photo(
                photo=FSInputFile(image_path),
                caption=f"📷 Назва: `{image.filename}`,Головне:{image.main_image}",
                parse_mode="Markdown"
            )
        else:
            await callback.message.answer(f"⚠️ Зображення '{image.filename}' не знайдено на диску.")

    await callback.message.answer("🔧 Панель адміністратора", reply_markup=get_admin_command())


@router.callback_query(F.data == "add_new_image")
async def add_new_image(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🖼️ Скиньте зображення яке ви хочете завантажити:")
    await callback.message.answer(f"🔹 Для скасування натисніть /cancel")
    await state.set_state(ImageProcessor.waiting_for_image)


@router.message(StateFilter(ImageProcessor.waiting_for_image), F.photo)
async def handle_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    await state.update_data(file_info=file_info)

    await message.answer("✏️ Тепер напишіть назву для зображення:")
    await message.answer("🔹 Для скасування натисніть /cancel")

    await state.set_state(ImageProcessor.waiting_for_title_image)


@router.message(ImageProcessor.waiting_for_title_image)
async def handle_image_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if title == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
        return

    data = await state.get_data()
    file_info = data.get("file_info")

    file_bytes = await message.bot.download_file(file_info.file_path)

    await save_image_to_disk_and_db(file_bytes, title)

    await state.clear()
    await message.answer("✅ Зображення збережено!", reply_markup=get_admin_command())


@router.callback_query(F.data == "add_new_text")
async def add_main_text(callback: CallbackQuery, state: FSMContext):
    """Обробка додавання нового тексту адміністратором"""

    await callback.message.answer("📝 Напишіть заголовок нового тексту:")
    await callback.message.answer(f"🔹 Для скасування натисніть /cancel")
    await state.set_state(NewEntry.waiting_for_title)


@router.message(NewEntry.waiting_for_title)
async def new_text_and_title(message: Message, state: FSMContext):
    """Збереження заголовка та запит тексту"""
    title = message.text.strip()
    if title == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
        return
    await state.update_data(title=title)
    await message.answer("📜 Напишіть сам текст:")
    await state.set_state(NewEntry.waiting_for_caption)


@router.message(NewEntry.waiting_for_caption)
async def save_new_entry(message: Message, state: FSMContext):
    """Збереження нового тексту після введення заголовка"""
    caption = message.text.strip()

    data = await state.get_data()
    title = data.get("title")
    if caption == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
        return
    outcome, msg = await add_caption(title, caption, main=False)

    await message.answer(msg)
    await state.clear()
    await message.answer("🔧 Панель адміністратора", reply_markup=get_admin_command())


@router.callback_query(F.data == "view_all_texts")
async def view_all_texts(callback: CallbackQuery):
    """Відображення всіх збережених текстів адміністратору"""
    captions = await get_all_captions()
    all_caption_text = ""
    if captions:
        for i, caption in enumerate(captions, start=1):
            all_caption_text += (
                f"📄 *Текст #{i}*\n"
                f"🔖 *Заголовок:* `{caption.title}`\n"
                f"📝 *Опис:* `{caption.caption}`\n"
                f"{'⭐️ ГОЛОВНИЙ ТЕКСТ ⭐️' if caption.main else '▪️Не головний'}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
            )
        await callback.message.answer(text="🗂 *Ось усі наявні тексти:*\n\n" + all_caption_text, parse_mode="Markdown",
                                      reply_markup=back_button_builder().as_markup())

    else:
        await callback.message.answer(
            "📭 Поки що жодного тексту не додано.",
            reply_markup=back_button_builder().as_markup()
        )


@router.callback_query(F.data == "select_main_text")
async def select_main_text(callback: CallbackQuery, state: FSMContext):
    text = (
        "📋  *Введіть заголовок тексту, який хочете зробити головним:*\n\n"
        f"🔹 Для скасування натисніть /cancel"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await state.set_state(NewEntry.waiting_for_main_text_title)


@router.message(NewEntry.waiting_for_main_text_title)
async def process_main_text_title(message: Message, state: FSMContext):
    title = message.text.strip()

    if title == "/cancel":
        # Якщо скасування, очищаємо стан
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
        return

    # Викликаємо функцію для зміни головного тексту
    main_captions = await main_captions_switch(title)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_text")],
            [InlineKeyboardButton(text="🔄 Ввести заголовок ще раз:", callback_data="select_main_text")],
        ])

    # Виводимо повідомлення користувачу
    if main_captions:
        await message.answer(main_captions, reply_markup=keyboard)

    # Очищаємо стан після виконання операції
    await state.clear()


@router.callback_query(F.data == "delete_text")
async def delete_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Введіть заголовок тексту, який хочете видалити:")
    await callback.message.answer(f"🔹 Для скасування натисніть /cancel")
    await state.set_state(NewEntry.waiting_for_header_removal)


@router.message(NewEntry.waiting_for_header_removal)
async def process_text_deletion(message: Message, state: FSMContext):
    title_delete = message.text.strip()

    if title_delete == "/cancel":
        # Якщо скасування, очищаємо стан
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
        return
    main_captions = await delete_captions(title_delete)
    if main_captions:
        await state.clear()
        await message.answer("✅ Текст вдало видалиний", reply_markup=get_admin_command())
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_text")],
                [InlineKeyboardButton(text="🔄 Ввести заголовок ще раз:", callback_data="delete_text")],
            ])
        await message.answer("❌ Заголовок не знайдено.", reply_markup=keyboard)


@router.message(F.text == "Перегляд зображеннь")
async def view_images_with_main(message: Message):
    await display_images(message, "Ось всі доступні зображення:", True)


@router.message(F.text == "Вибір головного зображення")
async def selecting_main_image(message: Message):
    await display_images(message, "Напишіть назву зображення, яке хочете зробити головним.")


@router.message(F.text == "Видалення зображення")
async def selecting_main_image(message: Message, state: FSMContext):
    await display_images(message, "✏ Напишіть назву зображення, яке хочете видалити.")
    await message.answer(f"🔹 Для скасування натисніть /cancel")
    await state.set_state(DeleteImageState.waiting_for_filename)


@router.message(DeleteImageState.waiting_for_filename)
async def delete_image(message: Message, state: FSMContext):
    """Обробка введеної назви зображення для видалення"""
    filename = message.text.strip()  # Отримуємо введене ім'я
    if filename.casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.")
        return
    success, msg = await delete_image_from_db(filename)

    if success:
        await message.answer(f"🗑️ {msg}")
    else:
        await message.answer(f"❌ {msg}")

    await state.clear()  # Скидаємо стан


@router.message(F.text == "Користувачі з БД")
async def greet(message: Message):
    """Виводить користувачів з бази даннних."""
    await message.answer("Ок, зараз відправлю...")
    users = await view_user()
    if users:
        text = "📋 *Список користувачів:*\n\n"
        text += "\n".join([
            f"🔹 *{i + 1}.* *Ім'я:* `{user.name}`\n   *Прізвище:* `{user.surname}`\n   *Нік:* `{user.login}`"
            for i, user in enumerate(users)
        ])
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("❌ Немає користувачів у базі.")


@router.message(F.text == "Додати заняття")
async def add_lesson(message: Message, state: FSMContext):
    """Функція для додавання заняття"""
    await message.answer("📝 Введіть тему заняття:\n\n🔹 Для скасування введіть /cancel")
    await state.set_state(LessonFactory.waiting_for_title)


@router.message(LessonFactory.waiting_for_title)
async def get_lesson_title(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    await state.update_data(title=message.text.strip())
    await message.answer("📅 Введіть дату заняття у форматі РРРР-ММ-ДД:")
    await state.set_state(LessonFactory.waiting_for_date)


@router.message(LessonFactory.waiting_for_date)
async def get_lesson_date(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    try:
        year, month, day = map(int, message.text.split("-"))
        await state.update_data(year=year, month=month, day=day)
        await message.answer("⏰ Введіть час заняття у форматі ГГ:ХХ:")
        await state.set_state(LessonFactory.waiting_for_time)
    except ValueError:
        await message.answer("⚠ Невірний формат! Введіть дату у форматі РРРР-ММ-ДД або /cancel для скасування.")


@router.message(LessonFactory.waiting_for_time)
async def get_lesson_time(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    try:
        hour, minute = map(int, message.text.split(":"))
        await state.update_data(hour=hour, minute=minute)

        # Вибір типу заняття
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🖥 Онлайн"), KeyboardButton(text="🏫 Офлайн")]
            ],
            resize_keyboard=True,
        )
        await message.answer("📌 Виберіть тип заняття:", reply_markup=keyboard)
        await state.set_state(LessonFactory.waiting_for_type)
    except ValueError:
        await message.answer("⚠ Невірний формат! Введіть час у форматі ГГ:ХХ або /cancel для скасування.")


@router.message(LessonFactory.waiting_for_type)
async def get_lesson_type(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    type_text = message.text.strip().lower()
    if "онлайн" in type_text:
        lesson_type = LessonType.ONLINE
    elif "офлайн" in type_text:
        lesson_type = LessonType.OFFLINE
    else:
        await message.answer("⚠ Невірний вибір! Виберіть '🖥 Онлайн' або '🏫 Офлайн'.")
        return

    await state.update_data(type_lesson=lesson_type)
    await message.answer("👥 Введіть кількість місць:")
    await state.set_state(LessonFactory.waiting_for_places)


@router.message(LessonFactory.waiting_for_places)
async def get_lesson_places(message: Message, state: FSMContext):
    if message.text.strip().casefold() == "/cancel":
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
        return
    try:
        places = int(message.text.strip())
        await state.update_data(places=places)

        # Отримуємо всі дані
        lesson_data = await state.get_data()

        # Створюємо заняття в БД
        await create_lesson(
            title=lesson_data["title"],
            year=lesson_data["year"],
            month=lesson_data["month"],
            day=lesson_data["day"],
            hour=lesson_data["hour"],
            minute=lesson_data["minute"],
            type_lesson=lesson_data["type_lesson"],
            places=lesson_data["places"]
        )

        await message.answer("✅ Заняття успішно створене!", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    except ValueError:
        await message.answer("⚠ Невірне значення! Введіть число або /cancel для скасування.")


@router.message(F.text.casefold() == "/cancel")
async def cancel_any_operation(message: Message, state: FSMContext):
    """Скасовує будь-яку операцію на будь-якому етапі"""
    current_state = await state.get_state()

    if current_state == NewEntry.waiting_for_title.state:
        await state.clear()
        await message.answer("❌ Операцію додавання заголовка скасовано.", reply_markup=ReplyKeyboardRemove())
        await message.answer("🔧 *Панель адміністратора*", parse_mode="Markdown", reply_markup=get_admin_command())
    else:
        await state.clear()
        await message.answer("❌ Операцію скасовано.", reply_markup=ReplyKeyboardRemove())


@router.message(Command("admin"))
async def admin_command(message: Message):
    unknown = message.from_user.id
    admin = await view_admins(unknown)

    if admin:
        await message.answer("🔧 *Панель адміністратора*", parse_mode="Markdown", reply_markup=get_admin_command())
    else:
        await message.answer("🚫 У вас немає прав доступу.")


@router.callback_query(F.data == "admin_admins")
async def go_to_main_menu(callback: CallbackQuery):
    admins = await view_admins()

    if not admins:
        await callback.message.answer("Адмінів немає")
        return

    all_admins_text = ""

    for i, admin in enumerate(admins, start=1):
        all_admins_text += (
            f"*Aдмін #{i}:*\n"
            f"👨‍💻 *Логін:* `{admin.login}`\n"
            f"🧑‍🏫 *Ім'я:* `{admin.name}`\n"
            f"👨‍🎓 *Прізвище:* `{admin.surname}`\n"
            f"🆔 *Telegram ID:* `{admin.tg_id}`\n"
            f"👑 *Головний адмін:* `{admin.main_admin}`\n"
            "-----------------------------------------\n"
        )
    await callback.message.answer(all_admins_text, parse_mode="Markdown",
                                  reply_markup=back_button_builder().as_markup())


@router.callback_query(F.data.in_({"user_count", "total_stats_user", "incomplete_signups"}))
async def go_to_main_menu(callback: CallbackQuery):
    users = await view_users()

    if not users:
        await callback.message.answer("🚫 Користувачів немає")
        return

    if callback.data == "total_stats_user":
        await callback.message.answer(f"👥 Загальна кількість користувачів,яка запускала бота: *{len(users)}*\n",
                                      parse_mode="Markdown")
        return

    if callback.data == "incomplete_signups":
        users = await view_users(True)
        await callback.message.answer(f"🚫👥 Користувачі які не разу не записувалися на заняття: *{len(users)}*\n",
                                      parse_mode="Markdown")
        return

    all_users_text = ""

    for i, user in enumerate(users, start=1):
        all_users_text += (
            f"*Користувач #{i}:*\n"
            f"👨‍💻 *Логін:* `{user.login}`\n"
            f"🧑‍🏫 *Ім'я:* `{user.name}`\n"
            f"👨‍🎓 *Прізвище:* `{user.surname}`\n"
            f"🆔 *Telegram ID:* `{user.tg_id}`\n"
            f"🔐 *Комбо-рядок для реєстрації:*\n"
            f"`{user.login}|{user.name}|{user.surname}|{user.tg_id}`\n"
            "----------------------------------------\n"
        )
    await callback.message.answer(all_users_text, parse_mode="Markdown", reply_markup=back_button_builder().as_markup())


@router.callback_query(F.data == "admin_menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        text="Оберіть дію з меню адміністратора:",
        reply_markup=get_admin_command()
    )
