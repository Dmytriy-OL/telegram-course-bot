from aiogram import Router

from .menu import router as menu_router
from .create_lesson import router as create_lesson_router
from .view_lessons import router as view_lessons_router
from .remove_student import router as remove_student_router
from .add_student import router as add_student_router
from .edit_lesson import router as edit_lesson_router
router = Router()

router.include_routers(
    menu_router,
    create_lesson_router,
    view_lessons_router,
    remove_student_router,
    add_student_router,
    edit_lesson_router
)
