import logging
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from app.web.dependencies.auth_dependencies import validate_login_form
from app.database.core.models import User
from app.web.templates import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, user_or_response: User | HTMLResponse = Depends(validate_login_form)):
    if isinstance(user_or_response, HTMLResponse):
        return user_or_response

    request.session["user"] = user_or_response.email
    return RedirectResponse(url="/", status_code=303)
