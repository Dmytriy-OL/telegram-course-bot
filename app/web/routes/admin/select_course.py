import logging
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import List

from starlette.responses import JSONResponse

from app.database.crud.web.administrator.handle_administrator import all_administrators
from app.database.crud.web.corses.handle_courses import all_courses, create_module, \
    create_task_for_module, generate_answer, create_video_url, get_course_by_id
from app.database.crud.web.services.module_service import parse_video_data, save_videos, parse_tasks_data, save_tasks
from app.web.dependencies.auth_dependencies import validate_login_form
from app.database.core.models import User
from app.web.schemas.forms import CoursesForm
from app.web.templates import templates
from app.web.utils.image_handler import save_video_to_module_folder

router = APIRouter()


@router.get("/select_courses", response_class=HTMLResponse)
async def select_courses_get(request: Request):
    courses = await all_courses()
    courses_with_teacher = []

    for course in courses:
        teacher_full_name = f"{course.teacher.name} {course.teacher.surname}" if course.teacher else "Невідомий викладач"
        courses_with_teacher.append({
            "id": course.id,
            "title": course.title,
            "teacher_full_name": teacher_full_name
        })

    return templates.TemplateResponse(
        "select_course.html",
        {"request": request, "courses": courses_with_teacher}
    )


@router.post("/select_courses", response_class=HTMLResponse)
async def module_create_post(request: Request, course_id: int = Form(...)):
    redirect_url = f"/create_module_courses?course_id={course_id}"
    return RedirectResponse(url=redirect_url, status_code=303)
