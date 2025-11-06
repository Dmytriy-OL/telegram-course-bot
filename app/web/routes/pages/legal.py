from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.web.templates import templates

router = APIRouter()


@router.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse("legal/terms.html", {"request": request})


@router.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse("legal/privacy.html", {"request": request})
