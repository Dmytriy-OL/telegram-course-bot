from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse,RedirectResponse
import traceback
from app.database.core.models import User
from app.database.crud.web.repository.user_repo import update_user_data
from app.database.crud.web.services.teacher_application import  TeacherApplicationService
# from app.database.crud.web.teacher.handle_teacher import create_teacher_request
from app.database.crud.web.teacher.exceptions import TeacherApplicationError
from app.web.dependencies.auth_dependencies import get_authenticated_user
from app.web.dependencies.teacher import get_teacher_application_service
from app.web.dependencies.template_dependencies import get_session_user, get_current_user, get_current_teacher
from app.web.schemas.teacher import TeacherApplicationCreate, TeacherLanguageCreate
from app.web.templates import templates
from app.web.utils.render import render

router = APIRouter()


@router.get("/become-teacher", response_class=HTMLResponse)
async def become_teacher(request: Request, user=Depends(get_session_user)):
    return templates.TemplateResponse(
        "teacher/become-teacher.html",
        {"request": request, "user": user}
    )


@router.get("/become_teacher", response_class=HTMLResponse)
async def get_become_teacher(request: Request):
    return render(
        request,
        "teacher/teacher_applications.html"
    )


@router.post("/become_teacher", response_class=HTMLResponse)
async def post_become_teacher(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    language: str = Form(...),
    experience: str = Form(...),
    english_level: str = Form(...),
    price: float = Form(...),
    phone: str = Form(...),
    bio: str = Form(...),
    telegram: str | None = Form(None),
    instagram: str | None = Form(None),
    youtube: str | None = Form(None),
    user: User = Depends(get_authenticated_user),
    service: TeacherApplicationService = Depends(get_teacher_application_service)
):
    social_networks = {
        k: v for k, v in {
            "telegram": telegram,
            "instagram": instagram,
            "youtube": youtube
        }.items() if v
    }

    dto = TeacherApplicationCreate(
        name=name,
        surname=surname,
        experience=experience,
        phone=phone,
        bio=bio,
        social_networks=social_networks,
        languages=[TeacherLanguageCreate(
            language=language,
            level=english_level,
            price=price
        )]
    )

    try:
        await service.apply(user, dto)

    except TeacherApplicationError as e:
        return render(
            request,
            "teacher/teacher_applications.html",
            user=user,
            error=str(e)
        )

    return RedirectResponse("/application_submitted", status_code=303)


@router.get("/application_submitted", response_class=HTMLResponse)
async def application_submitted(request: Request, teacher=Depends(get_current_teacher)):
    return render(request, "teacher/application_submitted.html", teacher=teacher)
