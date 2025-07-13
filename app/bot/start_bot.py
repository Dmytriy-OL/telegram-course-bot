import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.bot.handlers import router
from app.database.core.db_setup import create_tables
from app.database.core.config import DB_PATH


async def start_bot():
    if not os.path.exists(DB_PATH):
        print("☑️ Файл бази даних не знайдено, створюємо нові таблиці...")
        await create_tables()
    else:
        print("✅ Файл бази даних існує, пропускаємо створення таблиць.")

    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

