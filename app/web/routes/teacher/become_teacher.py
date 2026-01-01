from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse

from app.web.dependencies.template_dependencies import get_template_user
from app.web.templates import templates
from app.web.utils.render import render

router = APIRouter()


@router.get("/become-teacher", response_class=HTMLResponse)
async def become_teacher(request: Request, user=Depends(get_template_user)):
    return templates.TemplateResponse(
        "teacher/become-teacher.html",
        {"request": request, "user": user}
    )


@router.get("/become_teacher", response_class=HTMLResponse)
async def get_become_teacher(request: Request):
    return render(request, "teacher/become_teacher.html")


@router.post("/become_teacher", response_class=HTMLResponse)
async def post_become_teacher(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    language: str = Form(...),
    experience: str = Form(...),
    english_level: str = Form(...),
    price: int = Form(...),
    phone: str = Form(...),
    bio: str = Form(...),
    telegram: str | None = Form(None),
    instagram: str | None = Form(None),
    youtube: str | None = Form(None),
):
    social_networks = {
        k: v for k, v in {
            "telegram": telegram,
            "instagram": instagram,
            "youtube": youtube,
        }.items() if v
    }

    data = {
        "name": name,
        "surname": surname,
        "language": language,
        "experience": experience,
        "english_level": english_level,
        "price": price,
        "phone": phone,
        "bio": bio,
        "social_networks": social_networks
        # "status": "pending"
    }

    # create_teacher_request(**data)

    return render(
        request,
        "teacher/application_submitted.html"
    )

