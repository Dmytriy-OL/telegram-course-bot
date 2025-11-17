import logging
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from app.web.dependencies.auth_dependencies import parse_register_form
from werkzeug.security import generate_password_hash
from app.database.crud.web.repository.user_repo import validate_user_unique, save_user, confirm_email, \
    pending_user, get_user_by_email, update_user_google_id
from app.web.schemas.forms import RegisterForm
from app.web.templates import templates
from app.web.utils.tokens import verify_token
from .google_oauth import oauth

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request, "form_values": {}})


@router.post("/register", response_class=HTMLResponse)
async def register_post(
        request: Request,
        form_data: RegisterForm = Depends(parse_register_form),
):
    if isinstance(form_data, dict) and "error" in form_data:
        form = await request.form()
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": form_data["error"],
                "form_values": {
                    "email": form.get("email"),
                    "terms": form.get("terms") == "on"
                }
            }
        )
    form_values = form_data.model_dump()
    try:
        await validate_user_unique(
            form_data.email,
            # form_data.username
        )
    except ValueError as e:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": str(e),
                "form_values": form_values
            }
        )

    # birth_date = form_data.birth_date
    password_hash = generate_password_hash(form_data.password)

    # підтвердження ектроной адреси занесення в тимчасову базу даних,поки непідтвердить електрону адресу

    try:
        await pending_user(email=form_data.email,
                           # username=form_data.username,
                           password_hash=password_hash,
                           # birth_date=birth_date
                           )
    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": str(e),
                "form_values": form_values
            }
        )

    # підтвердження ектроной адреси
    # token = generate_token(form_data.email)
    # send_verification_email(form_data.email, token)
    # return templates.TemplateResponse("register.html", {
    #     "request": request,
    #     "form_values": form_data.model_dump(),
    #     "email_sent": True,
    #     "email": form_data.email
    # })

    # без підтвердження
    await confirm_email(form_data.email)
    request.session["user"] = {"email": form_data.email}
    return RedirectResponse(url="/profile/profile_setup", status_code=303)
