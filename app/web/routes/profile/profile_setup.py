from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database.crud.web.repository.user_repo import update_user_name
from app.web.templates import templates

router = APIRouter()


@router.get("/profile/profile_setup", response_class=HTMLResponse)
async def profile_setup_get(request: Request):
    user = request.session.get("user")
    email = user.get("email") if user else None

    if not email:
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        "auth/profile_setup.html",
        {"request": request, "error": None}
    )


@router.post("/profile/profile_setup", response_class=HTMLResponse)
async def profile_setup_post(
        request: Request,
        name: str = Form(...),
        surname: str = Form(...)
):
    user = request.session.get("user")
    email = user.get("email") if user else None
    if not email:
        return RedirectResponse("/login")

    if len(name) < 2 or len(surname) < 2:
        return templates.TemplateResponse(
            "auth/profile_setup.html",
            {"request": request, "error": "Заповніть імʼя та прізвище правильно!"}
        )

    await update_user_name(email, name, surname)

    request.session["user"] = {
        "email": email,
        "name": name,
        "surname": surname
    }

    return RedirectResponse("/", status_code=303)
