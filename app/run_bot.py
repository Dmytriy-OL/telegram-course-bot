import asyncio
from app.bot.start_bot import start_bot

if __name__ == "__main__":
    try:
        print('🚀 Telegram-бот запущений')
        asyncio.run(start_bot())

    except KeyboardInterrupt:
        print("Бот виключений")
