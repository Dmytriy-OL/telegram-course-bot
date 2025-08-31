import logging
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from werkzeug.security import generate_password_hash

from app.web.dependencies.auth_dependencies import validate_login_form
from app.database.core.models import User
from app.web.schemas.forms import PasswordForm
from app.web.templates import templates
from app.web.utils.tokens import generate_token, verify_token
from app.web.utils.email_sender import password_change_notification
from app.database.crud.web.repository.user_repo import user_exists, password_recovery

router = APIRouter()


@router.get("/forgot_password", response_class=HTMLResponse)
async def forgot_password_get(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.post("/forgot_password", response_class=HTMLResponse)
async def forgot_password_post(
        request: Request,
        email: str = Form(...),
):
    user_found = await user_exists(email)

    if user_found:
        message = "Ми надіслали посилання для відновлення пароля на електронну адресу."
        token = generate_token(email)
        password_change_notification(email, token)
        return templates.TemplateResponse(
            "forgot_password.html",
            {
                "request": request,
                "message": message,
                "form_values": {"email": email}
            }
        )
        # підтвердження ектроной адреси

    else:
        error = "Такої електронної адреси не існує."
    return templates.TemplateResponse(
        "forgot_password.html",
        {
            "request": request,
            "error": error,
            "form_values": {"email": email}
        }
    )


@router.get("/reset_password", response_class=HTMLResponse)
async def reset_password_get(request: Request, token: str):
    email = verify_token(token)
    if not email:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "success": False,
            "message": "Недійсний або прострочений токен"
        })
    # Показуємо форму
    return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "token": token
    })


@router.post("/reset_password", response_class=HTMLResponse)
async def reset_password_post(
        request: Request,
        token: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...)
):
    email = verify_token(token)

    if not email:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "success": False,
            "message": "Недійсний або прострочений токен"
        })

    try:
        form_data = PasswordForm(password=password, password_confirm=password_confirm, token=token)
    except ValueError as e:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "error": str(e)
        })

    password_hash = generate_password_hash(form_data.password)
    await password_recovery(email, password_hash)
    request.session["user"] = email
    return RedirectResponse(url="/", status_code=303)
