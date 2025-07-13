import asyncio
import threading

from app.bot.start_bot import start_bot
from app.web.start_web import run_flask


def start_web_in_thread():
    """Запускає Flask у окремому потоці"""
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()


async def main():
    start_web_in_thread()
    print("🚀 Запуск Telegram-бота...")
    await start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот зупинений")