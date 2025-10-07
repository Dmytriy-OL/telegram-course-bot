import logging
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse

from app.database.crud.web.administrator.handle_administrator import all_administrators
from app.database.crud.web.corses.handle_courses import create_course
from app.web.dependencies.auth_dependencies import validate_login_form
from app.database.core.models import User
from app.web.schemas.forms import CoursesForm
from app.web.templates import templates

router = APIRouter()


@router.get("/courses_add", response_class=HTMLResponse)
async def courses_add_get(request: Request):
    administrators = await all_administrators()
    return templates.TemplateResponse("courses_add.html", {"request": request,"teachers": administrators})


@router.post("/courses_add", response_class=HTMLResponse)
async def courses_add_post(request: Request,
                           title: str = Form(...),
                           price: int = Form(...),
                           caption: str = Form(...),
                           lesson_count: int = Form(...),
                           teacher_id: int = Form(...),
                           ):
    try:
        form_data = CoursesForm(price=price)
        await create_course(title, form_data.price, caption, lesson_count, teacher_id)
        return templates.TemplateResponse("courses_add.html", {
            "request": request,
            "success": "Курс успішно додано!",
        })
    except ValueError as e:
        return templates.TemplateResponse("courses_add.html", {
            "request": request,
            "error": str(e)
        })
