from pathlib import Path

# Абсолютний шлях до кореня "app"
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Папка для статичних файлів (тепер у web/static)
STATIC_DIR = BASE_DIR / "web" / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Папка для зберігання аватарок користувача
AVATAR_DIR = STATIC_DIR / "images" / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


# Папка для зберігання аватарок курсу
AVATAR_COURSES_DIR = STATIC_DIR / "images" / "courses_avatars"
AVATAR_COURSES_DIR.mkdir(parents=True, exist_ok=True)
