import logging
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import List
from app.database.crud.web.administrator.handle_administrator import all_administrators
from app.database.crud.web.corses.handle_courses import all_courses, create_module, \
    create_task_for_module, generate_answer, create_video_url
from app.database.crud.web.services.module_service import parse_video_data, save_videos, parse_tasks_data, save_tasks
from app.web.dependencies.auth_dependencies import validate_login_form
from app.database.core.models import User
from app.web.schemas.forms import CoursesForm
from app.web.templates import templates
from app.web.utils.image_handler import save_video_to_module_folder

router = APIRouter()


@router.get("/create_module_courses", response_class=HTMLResponse)
async def module_create_get(request: Request):
    administrators = await all_administrators()
    courses = await all_courses()
    return templates.TemplateResponse(
        "create_module_courses.html",
        {"request": request, "courses": courses, "teachers": administrators}
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
