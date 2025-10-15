import logging
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse

from app.database.crud.web.administrator.handle_administrator import all_administrators
from app.database.crud.web.corses.handle_courses import all_courses, create_module, \
    create_task_for_module, generate_answer
from app.web.dependencies.auth_dependencies import validate_login_form
from app.database.core.models import User
from app.web.schemas.forms import CoursesForm
from app.web.templates import templates

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
                             video_url: str = Form(...),
                             notes: str = Form(...),
                             order: int = Form(...),
                             is_active: bool = Form(...),
                             course_id: int = Form(...)
                             ):
    form = await request.form()
    tasks = {}
    module_id = await create_module(title, video_url, notes, order, is_active, course_id)

    for key, value in form.items():
        if key.startswith("tasks["):
            # приклад: tasks[1][answers][2][text]
            parts = key.replace("tasks[", "").replace("]", "").split("[")
            task_index = int(parts[0])
            field = parts[1]

            if task_index not in tasks:
                tasks[task_index] = {"question": None, "answers": []}

            if field == "question":
                tasks[task_index]["question"] = value
            elif field == "answers":
                ans_index = int(parts[2])
                ans_field = parts[3]
                while len(tasks[task_index]["answers"]) <= ans_index:
                    tasks[task_index]["answers"].append({})
                tasks[task_index]["answers"][ans_index][ans_field] = value
    if tasks:
        for task in tasks.values():
            task_id = await create_task_for_module(task["question"], None, module_id)
            for answer in task["answers"]:
                text = answer.get("text")
                is_correct = str(answer.get("is_correct")).lower() == "true"
                await generate_answer(text, is_correct, task_id)
                message = "Модуль успішно створено з завданнями."
    else:
        logging.info("Модуль створено без завдань")
        message = "Модуль успішно створено без завдань."

    return templates.TemplateResponse("create_module_courses.html", {
        "request": request,
        "success": message,
    })
