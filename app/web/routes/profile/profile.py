import os
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse
from datetime import datetime
from app.database.core.models import User
from app.database.crud.web.repository.user_repo import is_username_taken, update_user_data, update_user_avatar, \
 fetch_updated_user_with_avatar
from app.web.dependencies.auth_dependencies import get_authenticated_user
from app.web.templates import templates

from app.web.utils.image_handler import save_avatar_to_disk

router = APIRouter()


@router.get("/profile", response_class=HTMLResponse)
async def get_profile(
        request: Request,
        user: User = Depends(get_authenticated_user)
):
    if not user:
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "user": None, "error": "Користувач не знайдений!"}
        )

    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user}
    )


@router.post("/profile", response_class=HTMLResponse)
async def profile(
        request: Request,
        name: str = Form(...),
        surname: str = Form(...),
        username: str = Form(...),
        birth_date: str = Form(...),
        avatar: UploadFile = File(None),
        user: User = Depends(get_authenticated_user)
):
    try:
        birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "user": user, "error": "Невірний формат дати!"}
        )

    # Перевіряємо, чи зайнятий нікнейм
    if await is_username_taken(username, user.email):
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "user": user, "error": "Цей нікнейм вже зайнятий!"}
        )

    # Оновлюємо дані користувача
    updated_user = await update_user_data(user.email, name, surname, username, birth_date_obj)

    # Якщо є аватар — зберігаємо його
    if avatar and avatar.filename:
        file_name = await save_avatar_to_disk(avatar)
        await update_user_avatar(updated_user.id, file_name)

    # Підтягуємо оновлені дані разом з аватаром
    updated_user = await fetch_updated_user_with_avatar(updated_user)

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": updated_user,
            "message": "Дані змінено ✅"
        }
    )
