from aiogram import Router

# Імпортуємо маршрутизатори з файлів
from .commands import router as commands_router
from .admin import router as admin_router
from .callbacks import router as callbacks_router
# Створюємо загальний маршрутизатор
router = Router()


# Додаємо маршрутизатори команд та callback'ів до об'єднаного маршрутизатора
router.include_router(commands_router)
router.include_router(callbacks_router)
router.include_router(admin_router)