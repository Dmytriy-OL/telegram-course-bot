from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.web.templates import templates

router = APIRouter()


@router.get("/become-teacher", response_class=HTMLResponse)
async def become_teacher(request: Request):
    return templates.TemplateResponse(
        "pages/become-teacher.html",
        {"request": request}
    )