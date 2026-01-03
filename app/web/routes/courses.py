from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from app.database.crud.web.corses.handle_courses import all_courses
from app.web.dependencies.template_dependencies import get_session_user, get_current_user
from app.web.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@router.get("/main_page", response_class=HTMLResponse)
async def select_courses_get(request: Request, user=Depends(get_current_user)):
    courses = await all_courses()
    courses_with_teacher = []

    for course in courses:
        if course.avatar and course.avatar.file_name:
            avatar_url = f"/static/media/courses/{course.title}/courses_avatars/{course.avatar.file_name}"
        else:
            avatar_url = "/static/default_course.jpg"  # запасне зображення

        teacher_full_name = f"{course.teacher.name} {course.teacher.surname}" if course.teacher else "Невідомий викладач"
        courses_with_teacher.append({
            "id": course.id,
            "price": course.price,
            "lesson_count": course.lesson_count,
            "title": course.title,
            "teacher_full_name": teacher_full_name,
            "avatar_url": avatar_url
        })

    return templates.TemplateResponse(
        "main_page.html",
        {"request": request, "user": user, "courses": courses_with_teacher, "teachers": []}
    )


@router.post("/main_page", response_class=HTMLResponse)
async def module_create_post(request: Request, course_id: int = Form(...)):
    pass
