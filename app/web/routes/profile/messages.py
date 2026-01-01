import os
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse
from datetime import datetime
from app.database.core.models import User
from app.database.crud.web.repository.user_repo import is_username_taken, update_user_data, update_user_avatar, \
    fetch_updated_user_with_avatar
from app.web.dependencies.auth_dependencies import get_authenticated_user
from app.web.templates import templates

from app.web.utils.image_handler import save_image_to_disk_and_db

router = APIRouter()


@router.get("/profile/messages", response_class=HTMLResponse)
async def get_messager(
        request: Request,
        user: User = Depends(get_authenticated_user)
):
    return templates.TemplateResponse(
        "/profile/messages.html",
        {"request": request, "user": user}
    )
