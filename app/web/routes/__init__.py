from fastapi import APIRouter
from app.web.routes.register import router as router_register
from app.web.routes.profile import router as router_profile

router = APIRouter()

router.include_router(router_register)
router.include_router(router_profile)
