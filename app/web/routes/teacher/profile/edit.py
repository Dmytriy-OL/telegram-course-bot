from fastapi import APIRouter, Request, Depends, Form,UploadFile,File
from fastapi.responses import HTMLResponse, RedirectResponse
import traceback
from app.database.core.models import User
from app.database.crud.web.repository.user_repo import update_user_data
from app.database.crud.web.services.teacher_application import ProfileService
# from app.database.crud.web.teacher.handle_teacher import create_teacher_request
from app.database.crud.web.teacher.exceptions import TeacherApplicationError
from app.web.dependencies.auth_dependencies import get_authenticated_user
from app.web.dependencies.template_dependencies import get_current_user, get_current_teacher
from app.web.dependencies.user import get_profile_service
from app.web.schemas.teacher import TeacherApplicationCreate, ProfileUpdateData
from app.web.templates import templates
from app.web.utils.render import render

router = APIRouter()


@router.get("/profile/edit", response_class=HTMLResponse)
async def get_profile_promotion(request: Request, user=Depends(get_current_user), teacher=Depends(get_current_teacher)):
    return templates.TemplateResponse(
        "teacher/profile/profile_edit.html",
        {"request": request, "user": user, "teacher": teacher}
    )


@router.get("/profile/personal_edit", response_class=HTMLResponse)
async def get_personal_edit(request: Request, user=Depends(get_current_user), teacher=Depends(get_current_teacher)):
    return templates.TemplateResponse(
        "teacher/profile/profile_personal_edit.html",
        {"request": request, "user": user, "teacher": teacher}
    )


@router.put("/profile/personal_edit", response_class=HTMLResponse)
async def post_profile_settings(
        request: Request,
        first_name: str = Form(...),
        last_name: str = Form(...),
        avatar: UploadFile | None = File(None),
        user: User = Depends(get_authenticated_user),
        service: "ProfileService" = Depends(get_profile_service)
):
    # Створюємо DTO (дані для оновлення)
    data = ProfileUpdateData(first_name=first_name, last_name=last_name)

    # Викликаємо сервіс для оновлення профілю
    await service.update_profile(user, data, avatar)

    # Повертаємо шаблон із новими даними
    return RedirectResponse(
        url="/profile/personal_edit",
        status_code=303
    )
