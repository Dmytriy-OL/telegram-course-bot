from fastapi import APIRouter
from app.web.routes.auth.register import router as router_register
from app.web.routes.profile.profile import router as router_profile
from app.web.routes.profile.profile_setup import router as router_profile_setup
from app.web.routes.profile.profile_settings import router as profile_settings
from app.web.routes.profile.messages import router as messages
from app.web.routes.auth.login import router as router_login
from app.web.routes.forgot_password import router as router_forgot_password
from app.web.routes.courses import router as router_courses
from app.web.routes.admin.add_courses import router as admin_add_courses
from app.web.routes.admin.create_administrator import router as admin_add_administrator
from app.web.routes.admin.create_module_courses import router as create_module_courses
from app.web.routes.admin.select_course import router as select_course
from app.web.routes.teacher.become_teacher import router as become_teacher

from app.web.routes.pages.info import router as info
from app.web.routes.pages.legal import router as legal

from app.web.routes.auth.google_oauth import router as google_oauth

router = APIRouter()

router.include_router(router_register)
router.include_router(router_login)
router.include_router(google_oauth)

router.include_router(router_profile)
router.include_router(profile_settings)
router.include_router(router_profile_setup)
router.include_router(router_forgot_password)
router.include_router(router_courses)
router.include_router(messages)

router.include_router(admin_add_courses)
router.include_router(admin_add_administrator)
router.include_router(create_module_courses)
router.include_router(select_course)

router.include_router(become_teacher)

router.include_router(info)
router.include_router(legal)
