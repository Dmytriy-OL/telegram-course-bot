import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Отримуємо директорію поточного файлу
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")  # Формуємо шлях до бази

SQLALCHEMY_URL = f"sqlite+aiosqlite:///{DB_PATH}"