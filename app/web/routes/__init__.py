from fastapi import APIRouter
from app.web.routes.register import router as router_register
from app.web.routes.profile import router as router_profile
from app.web.routes.login import router as router_login
from app.web.routes.forgot_password import router as router_forgot_password

router = APIRouter()

router.include_router(router_register)
router.include_router(router_profile)
router.include_router(router_login)
router.include_router(router_forgot_password)
