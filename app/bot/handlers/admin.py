from aiogram.filters import StateFilter
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
# from app.database.crud.images import delete_image_from_db, view_user
# from app.handlers.utils import display_images
# from app.database.admin_crud import view_image

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


@router.callback_query(F.data == "admin_stats") # !!!
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








# @routes.callback_query(F.data == "select_main_image")
# async def select_main_image(callback: CallbackQuery, state: FSMContext):
#     images = await view_image()
#     if not images:
#         await callback.message.answer("❌ Зображень не знайдено.")
#         return
#     text_result = ""
#     for i, image in enumerate(images, start=1):
#         text_result += (
#             f"📄 *Зображення #{i}*\n"
#             f"🔖 *Назва зображення:* `{image.filename}`\n"
#             f"{'⭐️ ГОЛОВНЕ ЗОБРАЖЕННЯ ⭐️' if image.main_image else '▪️Не головне'}\n"
#             f"━━━━━━━━━━━━━━━━━━━━━━\n"
#         )
#     await callback.message.answer(text="🗂 *Ось усі назви зображень::*\n\n" + text_result, parse_mode="Markdown")
#     text = (
#         "📋  *Введіть назву малюнка, якого хочете зробити головним:*\n\n"
#         f"🔹 Для скасування натисніть /cancel"
#     )
#     await callback.message.answer(text, parse_mode="Markdown")
#     await state.set_state(ImageProcessor.waiting_for_main_title)


# @routes.message(ImageProcessor.waiting_for_main_title)
# async def process_main_image_title(message: Message, state: FSMContext):
#     title = message.text.strip()
#
#     if title == "/cancel":
#         # Якщо скасування, очищаємо стан
#         await state.clear()
#         await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
#         return
#
#     # Викликаємо функцію для зміни головного тексту
#     main_image = await main_image_switch(title)
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_text")],
#             [InlineKeyboardButton(text="🔄 Ввести заголовок ще раз:", callback_data="select_main_image")],
#         ])
#
#     # Виводимо повідомлення користувачу
#     if main_image:
#         await message.answer(main_image, reply_markup=keyboard)
#
#     # Очищаємо стан після виконання операції
#     await state.clear()


# @routes.callback_query(F.data == "delete_image")
# async def delete_image(callback: CallbackQuery, state: FSMContext):
#     images = await view_image()
#     if not images:
#         await callback.message.answer("❌ Зображень не знайдено.")
#         return
#     await state.update_data(images=images)
#     text_result = ""
#     for i, image in enumerate(images, start=1):
#         text_result += (
#             f"📄 *Зображення #{i}*\n"
#             f"🔖 *Назва зображення:* `{image.filename}`\n"
#             f"{'⭐️ ГОЛОВНЕ ЗОБРАЖЕННЯ ⭐️' if image.main_image else '▪️Не головне'}\n"
#             f"━━━━━━━━━━━━━━━━━━━━━━\n"
#         )
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_image")],
#             [InlineKeyboardButton(text="🗑️ Видалити зображення:", callback_data="filename_delete")],
#         ])
#     await callback.message.answer(text="🗂 *Ось усі назви зображень::*\n\n" + text_result, parse_mode="Markdown",
#                                   reply_markup=keyboard)


@router.callback_query(F.data == "filename_delete")
async def filename_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введіть назву зображення, яке хочете видалити 🗑️️")
    await state.set_state(ImageProcessor.waiting_for_delete_image)


# @routes.message(ImageProcessor.waiting_for_delete_image)
# async def delete_image_title(message: Message, state: FSMContext):
#     title = message.text.strip()
#     data = await state.get_data()
#     images = data.get("images")
#
#     for image in images:
#         if title == image.filename:
#             await delete_image_to_disk_and_db(title)
#             await state.clear()
#             await message.answer("✅ Зображення вдало видалено 🗑️", reply_markup=get_admin_command())
#             return
#
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_text")],
#             [InlineKeyboardButton(text="🔄 Ввести заголовок ще раз:", callback_data="filename_delete")],
#         ])
#     await message.answer(f"❌ Зображення `{title}` не знайдено.", parse_mode="Markdown", reply_markup=keyboard)


# @routes.callback_query(F.data == "view_all_image")
# async def view_all_image(callback: CallbackQuery):
#     images = await view_image()
#
#     if not images:
#         await callback.message.answer("❌ Зображень не знайдено.")
#         return
#
#     for image in images:
#         image_path = BASE_DIR / f"{image.filename}.jpg"
#
#         if image_path.exists():
#             await callback.message.answer_photo(
#                 photo=FSInputFile(image_path),
#                 caption=f"📷 Назва: `{image.filename}`,Головне:{image.main_image}",
#                 parse_mode="Markdown"
#             )
#         else:
#             await callback.message.answer(f"⚠️ Зображення '{image.filename}' не знайдено на диску.")
#
#     await callback.message.answer("🔧 Панель адміністратора", reply_markup=get_admin_command())


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


# @routes.message(ImageProcessor.waiting_for_title_image)
# async def handle_image_title(message: Message, state: FSMContext):
#     title = message.text.strip()
#     if title == "/cancel":
#         await state.clear()
#         await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
#         return
#
#     data = await state.get_data()
#     file_info = data.get("file_info")
#
#     file_bytes = await message.bot.download_file(file_info.file_path)
#
#     await save_image_to_disk_and_db(file_bytes, title)
#
#     await state.clear()
#     await message.answer("✅ Зображення збережено!", reply_markup=get_admin_command())


@router.callback_query(F.data == "add_new_text")
async def add_main_text(callback: CallbackQuery, state: FSMContext):
    """Обробка додавання нового тексту адміністратором"""

    await callback.message.answer("📝 Напишіть заголовок нового тексту:")
    await callback.message.answer(f"🔹 Для скасування натисніть /cancel")
    await state.set_state(NewEntry.waiting_for_title)


# @routes.message(NewEntry.waiting_for_title)
# async def new_text_and_title(message: Message, state: FSMContext):
#     """Збереження заголовка та запит тексту"""
#     title = message.text.strip()
#     if title == "/cancel":
#         await state.clear()
#         await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
#         return
#     await state.update_data(title=title)
#     await message.answer("📜 Напишіть сам текст:")
#     await state.set_state(NewEntry.waiting_for_caption)


# @routes.message(NewEntry.waiting_for_caption)
# async def save_new_entry(message: Message, state: FSMContext):
#     """Збереження нового тексту після введення заголовка"""
#     caption = message.text.strip()
#
#     data = await state.get_data()
#     title = data.get("title")
#     if caption == "/cancel":
#         await state.clear()
#         await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
#         return
#     outcome, msg = await add_caption(title, caption, main=False)
#
#     await message.answer(msg)
#     await state.clear()
#     await message.answer("🔧 Панель адміністратора", reply_markup=get_admin_command())


# @routes.callback_query(F.data == "view_all_texts")
# async def view_all_texts(callback: CallbackQuery):
#     """Відображення всіх збережених текстів адміністратору"""
#     captions = await get_all_captions()
#     all_caption_text = ""
#     if captions:
#         for i, caption in enumerate(captions, start=1):
#             all_caption_text += (
#                 f"📄 *Текст #{i}*\n"
#                 f"🔖 *Заголовок:* `{caption.title}`\n"
#                 f"📝 *Опис:* `{caption.caption}`\n"
#                 f"{'⭐️ ГОЛОВНИЙ ТЕКСТ ⭐️' if caption.main else '▪️Не головний'}\n"
#                 f"━━━━━━━━━━━━━━━━━━━━━━\n"
#             )
#         await callback.message.answer(text="🗂 *Ось усі наявні тексти:*\n\n" + all_caption_text, parse_mode="Markdown",
#                                       reply_markup=back_button_builder().as_markup())
#
#     else:
#         await callback.message.answer(
#             "📭 Поки що жодного тексту не додано.",
#             reply_markup=back_button_builder().as_markup()
#         )


@router.callback_query(F.data == "select_main_text")
async def select_main_text(callback: CallbackQuery, state: FSMContext):
    text = (
        "📋  *Введіть заголовок тексту, який хочете зробити головним:*\n\n"
        f"🔹 Для скасування натисніть /cancel"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await state.set_state(NewEntry.waiting_for_main_text_title)


# @routes.message(NewEntry.waiting_for_main_text_title)
# async def process_main_text_title(message: Message, state: FSMContext):
#     title = message.text.strip()
#
#     if title == "/cancel":
#         # Якщо скасування, очищаємо стан
#         await state.clear()
#         await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
#         return
#
#     # Викликаємо функцію для зміни головного тексту
#     main_captions = await main_captions_switch(title)
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_text")],
#             [InlineKeyboardButton(text="🔄 Ввести заголовок ще раз:", callback_data="select_main_text")],
#         ])
#
#     # Виводимо повідомлення користувачу
#     if main_captions:
#         await message.answer(main_captions, reply_markup=keyboard)
#
#     # Очищаємо стан після виконання операції
#     await state.clear()


@router.callback_query(F.data == "delete_text")
async def delete_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Введіть заголовок тексту, який хочете видалити:")
    await callback.message.answer(f"🔹 Для скасування натисніть /cancel")
    await state.set_state(NewEntry.waiting_for_header_removal)


# @routes.message(NewEntry.waiting_for_header_removal)
# async def process_text_deletion(message: Message, state: FSMContext):
#     title_delete = message.text.strip()
#
#     if title_delete == "/cancel":
#         # Якщо скасування, очищаємо стан
#         await state.clear()
#         await message.answer("❌ Операцію скасовано.", reply_markup=get_admin_command())
#         return
#     main_captions = await delete_captions(title_delete)
#     if main_captions:
#         await state.clear()
#         await message.answer("✅ Текст вдало видалиний", reply_markup=get_admin_command())
#     else:
#         keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text="🔙 Повернутись до адмін меню", callback_data="edit_main_text")],
#                 [InlineKeyboardButton(text="🔄 Ввести заголовок ще раз:", callback_data="delete_text")],
#             ])
#         await message.answer("❌ Заголовок не знайдено.", reply_markup=keyboard)

#
# @routes.message(F.text == "Перегляд зображеннь")
# async def view_images_with_main(message: Message):
#     await display_images(message, "Ось всі доступні зображення:", True)
#
#
# @routes.message(F.text == "Вибір головного зображення")
# async def selecting_main_image(message: Message):
#     await display_images(message, "Напишіть назву зображення, яке хочете зробити головним.")
#
#
# @routes.message(F.text == "Видалення зображення")
# async def selecting_main_image(message: Message, state: FSMContext):
#     await display_images(message, "✏ Напишіть назву зображення, яке хочете видалити.")
#     await message.answer(f"🔹 Для скасування натисніть /cancel")
#     await state.set_state(DeleteImageState.waiting_for_filename)
#
#
# @routes.message(DeleteImageState.waiting_for_filename)
# async def delete_image(message: Message, state: FSMContext):
#     """Обробка введеної назви зображення для видалення"""
#     filename = message.text.strip()  # Отримуємо введене ім'я
#     if filename.casefold() == "/cancel":
#         await state.clear()
#         await message.answer("❌ Операцію скасовано.")
#         return
#     success, msg = await delete_image_from_db(filename)
#
#     if success:
#         await message.answer(f"🗑️ {msg}")
#     else:
#         await message.answer(f"❌ {msg}")
#
#     await state.clear()  # Скидаємо стан
#
#
# @routes.message(F.text == "Користувачі з БД")
# async def greet(message: Message):
#     """Виводить користувачів з бази даннних."""
#     await message.answer("Ок, зараз відправлю...")
#     users = await view_user()
#     if users:
#         text = "📋 *Список користувачів:*\n\n"
#         text += "\n".join([
#             f"🔹 *{i + 1}.* *Ім'я:* `{user.name}`\n   *Прізвище:* `{user.surname}`\n   *Нік:* `{user.login}`"
#             for i, user in enumerate(users)
#         ])
#         await message.answer(text, parse_mode="Markdown")
#     else:
#         await message.answer("❌ Немає користувачів у базі.")
#











# @routes.callback_query(F.data == "admin_admins")
# async def go_to_main_menu(callback: CallbackQuery):
#     admins = await view_admins()
#
#     if not admins:
#         await callback.message.answer("Адмінів немає")
#         return
#
#     all_admins_text = ""
#
#     for i, admin in enumerate(admins, start=1):
#         all_admins_text += (
#             f"*Aдмін #{i}:*\n"
#             f"👨‍💻 *Логін:* `{admin.login}`\n"
#             f"🧑‍🏫 *Ім'я:* `{admin.name}`\n"
#             f"👨‍🎓 *Прізвище:* `{admin.surname}`\n"
#             f"🆔 *Telegram ID:* `{admin.tg_id}`\n"
#             f"👑 *Головний адмін:* `{admin.main_admin}`\n"
#             "-----------------------------------------\n"
#         )
#     await callback.message.answer(all_admins_text, parse_mode="Markdown",
#                                   reply_markup=back_button_builder().as_markup())


# @routes.callback_query(F.data.in_({"user_count", "total_stats_user", "incomplete_signups"}))
# async def go_to_main_menu(callback: CallbackQuery):
#     users = await view_users()
#
#     if not users:
#         await callback.message.answer("🚫 Користувачів немає")
#         return
#
#     if callback.data == "total_stats_user":
#         await callback.message.answer(f"👥 Загальна кількість користувачів,яка запускала бота: *{len(users)}*\n",
#                                       parse_mode="Markdown")
#         return
#
#     if callback.data == "incomplete_signups":
#         users = await view_users(True)
#         await callback.message.answer(f"🚫👥 Користувачі які не разу не записувалися на заняття: *{len(users)}*\n",
#                                       parse_mode="Markdown")
#         return
#
#     all_users_text = ""
#
#     for i, user in enumerate(users, start=1):
#         all_users_text += (
#             f"*Користувач #{i}:*\n"
#             f"👨‍💻 *Логін:* `{user.login}`\n"
#             f"🧑‍🏫 *Ім'я:* `{user.name}`\n"
#             f"👨‍🎓 *Прізвище:* `{user.surname}`\n"
#             f"🆔 *Telegram ID:* `{user.tg_id}`\n"
#             f"🔐 *Комбо-рядок для реєстрації:*\n"
#             f"`{user.login}|{user.name}|{user.surname}|{user.tg_id}`\n"
#             "----------------------------------------\n"
#         )
#     await callback.message.answer(all_users_text, parse_mode="Markdown", reply_markup=back_button_builder().as_markup())


