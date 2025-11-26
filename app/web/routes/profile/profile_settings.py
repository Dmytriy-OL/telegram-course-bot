from fastapi import APIRouter, Request, Form, Depends, UploadFile,File
from fastapi.responses import HTMLResponse, RedirectResponse
from werkzeug.security import generate_password_hash

from app.database.core.models import User
from app.database.crud.web.repository.user_repo import get_user_by_email, update_user_data, update_user_avatar, \
    fetch_updated_user_with_avatar, get_password_hash, update_user_password
from app.web.dependencies.auth_dependencies import get_current_user, get_authenticated_user
from app.web.templates import templates
from app.web.dependencies.parse_profile_form import parse_profile_form, ChangePasswordForm, parse_change_password_form, \
    check_password
from app.web.utils.email_sender import password_change_notification
from app.web.utils.image_handler import save_image_to_disk_and_db
from app.web.utils.tokens import generate_token

router = APIRouter()


@router.get("/profile/profile_settings", response_class=HTMLResponse)
async def get_profile_settings(
        request: Request,
        user=Depends(get_current_user)
):
    return templates.TemplateResponse(
        "profile/profile_settings.html",
        {"request": request, "user": user}
    )


@router.post("/settings/update_profile", response_class=HTMLResponse)
async def post_profile_settings(
        request: Request,
        user=Depends(parse_profile_form),
        current_user: User = Depends(get_authenticated_user)
):
    updated_user = await update_user_data(current_user.id, user.name, user.surname, user.username, user.birth_date)
    return templates.TemplateResponse(
        "profile/profile_settings.html",
        {
            "request": request,
            "user": updated_user
        }
    )


@router.post("/settings/upload_avatar")
async def upload_avatar(
    request: Request,
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_authenticated_user)
):
    if avatar and avatar.filename:
        file_name = await save_image_to_disk_and_db(avatar)
        await update_user_avatar(current_user.id, file_name)

    return RedirectResponse(
        url="/profile/profile_settings#avatar",
        status_code=303
    )


@router.post("/settings/change_password")
async def change_password(
    request: Request,
    current_user: User = Depends(get_authenticated_user),
    form: ChangePasswordForm = Depends(parse_change_password_form)
):
    password_hash = await get_password_hash(current_user.id)

    if not password_hash:
        return RedirectResponse(
            url="/profile/profile_settings?error=no_password#security",
            status_code=303
        )

    is_valid = await check_password(password_hash, form.old_password)

    if not is_valid:
        return RedirectResponse(
            url="/profile/profile_settings?error=wrong_password#security",
            status_code=303
        )

    new_hash = generate_password_hash(form.new_password)
    await update_user_password(current_user.id, new_hash)

    return RedirectResponse(
        url="/profile/profile_settings?success=password_changed#security",
        status_code=303
    )


@router.post("/settings/forgot-password")
async def forgot_password(current_user: User = Depends(get_authenticated_user)):
    email = current_user.email

    token = generate_token(email)
    password_change_notification(email, token)

    return {"status": "email_sent"}
