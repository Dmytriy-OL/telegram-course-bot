import logging
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import List

from starlette.responses import JSONResponse

from app.database.crud.web.administrator.handle_administrator import all_administrators
from app.database.crud.web.corses.handle_courses import all_courses, create_module, \
    create_task_for_module, generate_answer, create_video_url, get_course_by_id, get_used_lessons_for_course
from app.database.crud.web.services.module_service import parse_video_data, save_videos, parse_tasks_data, save_tasks
from app.web.dependencies.auth_dependencies import validate_login_form
from app.database.core.models import User
from app.web.schemas.forms import CoursesForm
from app.web.templates import templates
from app.web.utils.image_handler import save_video_to_module_folder

router = APIRouter()


@router.get("/create_module_courses", response_class=HTMLResponse)
async def create_module_get(request: Request, course_id: int):
    administrators = await all_administrators()
    course = await get_course_by_id(course_id)

    if not course:
        return templates.TemplateResponse(
            "create_module_courses.html",
            {"request": request, "error": "Курс не знайдено."}
        )

    used_orders = await get_used_lessons_for_course(course_id)
    available_orders = [i for i in range(1, course.lesson_count + 1) if i not in used_orders]

    return templates.TemplateResponse(
        "create_module_courses.html",
        {
            "request": request,
            "course": course,
            "teachers": administrators,
            "available_orders": available_orders
        }
    )


@router.post("/create_module_courses", response_class=HTMLResponse)
async def module_create_post(request: Request,
                             title: str = Form(...),
                             notes: str = Form(...),
                             order: int = Form(...),
                             is_active: bool = Form(...),
                             course_id: int = Form(...),
                             videos_file: List[UploadFile] = File(None),
                             videos_description: List[str] = Form(None),
                             ):
    form = await request.form()
    message = ""

    try:
        module_id = await create_module(title, notes, order, is_active, course_id)
        message += "Модуль створено. "

        videos_data_url = parse_video_data(form)
        if videos_data_url:
            await save_videos(videos_data_url, module_id)
            message += "🎥 Посилання на відео збережено. "

        # обробка відео
        if videos_file and videos_description:
            for video, description in zip(videos_file, videos_description):
                await save_video_to_module_folder(video, description, course_id, module_id)
            message += f"🎥 Завантажено {len(videos_file)} відео. "

        tasks_data = parse_tasks_data(form)
        if tasks_data:
            await save_tasks(tasks_data, module_id)
            message += " Завдання вдало створено"
        else:
            logging.info("Модуль створено без завдань")
            message += " Модуль успішно створено без завдань."

    except HTTPException as e:
        return templates.TemplateResponse("create_module_courses.html", {
            "request": request,
            "error": e.detail
        })

    except Exception as e:
        logging.error(f"Невідома помилка: {e}")
        return templates.TemplateResponse("create_module_courses.html", {
            "request": request,
            "error": "❌ Сталася непередбачена помилка. Спробуйте пізніше."
        })

    return templates.TemplateResponse("create_module_courses.html", {
        "request": request,
        "message": message,
    })
