import logging
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse

from app.database.crud.web.administrator.handle_administrator import create_administrator
from app.web.dependencies.auth_dependencies import validate_login_form
from app.database.core.models import User
from app.web.schemas.forms import CoursesForm
from app.web.templates import templates

router = APIRouter()


@router.get("/create_administrator", response_class=HTMLResponse)
async def create_administrator_get(request: Request):
    return templates.TemplateResponse("create_administrator.html", {"request": request})


@router.post("/create_administrator", response_class=HTMLResponse)
async def create_administrator_post(request: Request,
                                    tg_id: int = Form(...),
                                    name: str = Form(...),
                                    surname: str = Form(...),
                                    login: str = Form(...),
                                    main_admin: bool = Form(...),
                                    ):
    try:
        await create_administrator(tg_id, name, surname, login, main_admin)
        return templates.TemplateResponse("create_administrator.html", {
            "request": request,
            "success": "Викладача успішно додано!",
        })
    except ValueError as e:
        return templates.TemplateResponse("create_administrator.html", {
            "request": request,
            "error": str(e)
        })
