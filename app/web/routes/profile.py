import os
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database.core.models import User
from app.web.dependencies.auth_dependencies import get_current_user
from app.web.templates import templates
router = APIRouter()


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})
