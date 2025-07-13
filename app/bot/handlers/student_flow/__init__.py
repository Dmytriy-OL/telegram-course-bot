from aiogram import Router

from .menu import router as menu_router
from .week_selector import router as week_selector_router
from .enroll import router as enroll_lessons_router
from .bookings import router as bookings_router

router = Router()

router.include_routers(
    menu_router,
    week_selector_router,
    enroll_lessons_router,
    bookings_router
)
