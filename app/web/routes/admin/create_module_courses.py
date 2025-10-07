import logging
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse

from app.database.crud.web.administrator.handle_administrator import all_administrators
from app.database.crud.web.corses.handle_courses import create_course, all_courses
from app.web.dependencies.auth_dependencies import validate_login_form
from app.database.core.models import User
from app.web.schemas.forms import CoursesForm
from app.web.templates import templates

router = APIRouter()


@router.get("/courses_module_add", response_class=HTMLResponse)
async def module_create_get(request: Request):
    administrators = await all_administrators()
    courses = await all_courses()
    return templates.TemplateResponse(
        "courses_module_add.html",
        {"request": request, "courses": courses, "teachers": administrators}
    )


@router.post("/courses_module_add", response_class=HTMLResponse)
async def module_create_post(request: Request,
                             title: str = Form(...),
                             video_url: str = Form(...),
                             notes: str = Form(...),
                             assignment: str = Form(...),
                             order: int = Form(...),
                             is_active: bool = Form(...),
                             courses_id: int = Form(...)
                             ):
    try:
        # await create_course(title, form_data.price, caption, lesson_count, teacher_id)
        return templates.TemplateResponse("courses_module_add.html", {
            "request": request,
            "success": "Курс успішно додано!",
        })
    except ValueError as e:
        return templates.TemplateResponse("courses_add.html", {
            "request": request,
            "error": str(e)
        })


1
