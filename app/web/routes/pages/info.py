from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.web.templates import templates

router = APIRouter()


@router.get("/learn-more", response_class=HTMLResponse)
async def learn_more(request: Request):
    return templates.TemplateResponse(
        "learn_more.html",
        {"request": request}
    )
