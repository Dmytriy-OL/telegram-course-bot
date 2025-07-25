import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.bot.handlers import router
from app.database.core.db_setup import create_tables

load_dotenv()


async def start_bot():
    try:
        print("☑️ Перевіряємо/створюємо таблиці в базі даних...")
        await create_tables()
        print("✅ Таблиці готові.")
    except Exception as e:
        print(f"❌ Помилка при створенні таблиць: {e}")
        raise

    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)
