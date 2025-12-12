from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from werkzeug.security import generate_password_hash

from app.web.schemas.forms import PasswordForm
from app.web.templates import templates
from app.web.utils.tokens import generate_token, verify_token
from app.web.utils.email_sender import password_change_notification
from app.database.crud.web.repository.user_repo import user_exists, password_recovery

router = APIRouter()


@router.get("/forgot_password_sent", response_class=HTMLResponse)
async def forgot_password_sent(request: Request):
    return templates.TemplateResponse(
        "auth/forgot_password.html",
        {"request": request}
    )


@router.get("/forgot_password_form", response_class=HTMLResponse)
async def forgot_password_form_get(request: Request):

    error = None
    if request.query_params.get("error") == "not_found":
        error = "Такої електронної адреси не існує"

    return templates.TemplateResponse(
        "auth/forgot_password_form.html",
        {
            "request": request,
            "error": error
        }
    )


@router.post("/forgot_password")
async def forgot_password_form_post(email: str = Form(...)):
    user_found = await user_exists(email)

    if user_found:
        token = generate_token(email)
        password_change_notification(email, token)

        # 👇 Перекидаємо на сторінку "Лист надіслано"
        return RedirectResponse(
            url="/forgot_password_sent",
            status_code=303
        )

    return RedirectResponse(
        url="/forgot_password_form?error=not_found",
        status_code=303
    )


@router.get("/reset_password", response_class=HTMLResponse)
async def reset_password_get(request: Request, token: str):
    email = verify_token(token)
    if not email:
        return templates.TemplateResponse("profile/reset_password.html", {
            "request": request,
            "success": False,
            "message": "Недійсний або прострочений токен"
        })
    # Показуємо форму
    return templates.TemplateResponse("profile/reset_password.html", {
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
        return templates.TemplateResponse("profile/reset_password.html", {
            "request": request,
            "success": False,
            "message": "Недійсний або прострочений токен"
        })

    try:
        form_data = PasswordForm(password=password, password_confirm=password_confirm, token=token)
    except ValueError as e:
        return templates.TemplateResponse("profile/reset_password.html", {
            "request": request,
            "token": token,
            "error": str(e)
        })

    password_hash = generate_password_hash(form_data.password)
    await password_recovery(email, password_hash)
    request.session["user"] = email
    return RedirectResponse(url="/", status_code=303)


