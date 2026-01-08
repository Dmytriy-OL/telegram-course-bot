from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import traceback
from app.database.core.models import User
from app.database.crud.web.repository.user_repo import update_user_data
# from app.database.crud.web.teacher.handle_teacher import create_teacher_request
from app.database.crud.web.teacher.exceptions import TeacherApplicationError
from app.web.dependencies.auth_dependencies import get_authenticated_user
from app.web.dependencies.template_dependencies import get_current_user, get_current_teacher
from app.web.schemas.teacher import TeacherApplicationCreate
from app.web.templates import templates
from app.web.utils.render import render

router = APIRouter()


@router.get("/help/profile_promotion", response_class=HTMLResponse)
async def get_profile_promotion(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse(
        "teacher/help/profile_promotion.html",
        {"request": request, "user": user}
    )

