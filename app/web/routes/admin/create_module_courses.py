import logging
from typing import List

from fastapi import APIRouter, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse

from app.database.crud.web.administrator.handle_administrator import all_administrators
from app.database.crud.web.corses.handle_courses import create_module, get_course_by_id, get_used_lessons_for_course
from app.database.crud.web.services.module_service import parse_video_data, save_videos, parse_tasks_data, save_tasks
from app.web.templates import templates
from app.web.utils.image_handler import save_video_to_module_folder

router = APIRouter()


@router.get("/create_module_courses", response_class=HTMLResponse)
async def create_module_get(
        request: Request,
        course_id: int,
        message: str = None,
        error: str = None
):
    course = await get_course_by_id(course_id)
    if not course:
        return RedirectResponse(url="/select_courses", status_code=303)

    used_orders = await get_used_lessons_for_course(course_id)
    next_order = max(used_orders, default=0) + 1

    if next_order > course.lesson_count:
        return templates.TemplateResponse(
            "create_module_courses.html",
            {
                "request": request,
                "course": course,
                "teachers": await all_administrators(),
                "next_order": next_order,
                "message": message,
                "error": error
            }
        )


@router.post("/create_module_courses", response_class=HTMLResponse)
async def module_create_post(
        request: Request,
        title: str = Form(...),
        notes: str = Form(...),
        order: int = Form(...),
        is_active: bool = Form(...),
        course_id: int = Form(...),
        videos_file: List[UploadFile] = File(None),
        videos_description: List[str] = Form(None),
):
    try:
        course = await get_course_by_id(course_id)
        used_orders = await get_used_lessons_for_course(course_id)
        next_order = max(used_orders, default=0) + 1

        if next_order > course.lesson_count:
            return templates.TemplateResponse(
                "create_module_courses.html",
                {
                    "request": request,
                    "course": course,
                    "teachers": await all_administrators(),
                    "next_order": next_order,
                    "error": "Досягнуто максимальної кількості модулів для курсу."
                }
            )

        module_id = await create_module(title, notes, order, is_active, course_id)

        # обробка посилань на відео
        form = await request.form()
        videos_data_url = parse_video_data(form)
        if videos_data_url:
            await save_videos(videos_data_url, module_id)

        # обробка завантажених відео
        if videos_file and videos_description:
            for video, description in zip(videos_file, videos_description):
                await save_video_to_module_folder(video, description, course_id, module_id)

        # обробка завдань
        tasks_data = parse_tasks_data(form)
        if tasks_data:
            await save_tasks(tasks_data, module_id)

    except HTTPException as e:
        # якщо помилка — показуємо її у GET-запиті
        return RedirectResponse(
            url=f"/create_module_courses?course_id={course_id}&error={e.detail}",
            status_code=303
        )

    except Exception as e:
        logging.error(f"Невідома помилка: {e}")
        return RedirectResponse(
            url=f"/create_module_courses?course_id={course_id}&error=Непередбачена помилка",
            status_code=303
        )

    # успішне створення модуля — редіректимо на ту ж сторінку (GET)
    return RedirectResponse(url=f"/create_module_courses?course_id={course_id}&message=Модуль створено",
                            status_code=303)
