from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from app.web.dependencies.template_dependencies import get_session_user
from app.web.templates import templates

router = APIRouter()


@router.get("/learn-more", response_class=HTMLResponse)
async def learn_more(request: Request, user=Depends(get_session_user)):
    return templates.TemplateResponse(
        "pages/learn_more.html",
        {"request": request, "user": user}
    )


@router.get("/why_us", response_class=HTMLResponse)
async def learn_more(request: Request, user=Depends(get_session_user)):
    return templates.TemplateResponse(
        "pages/why_us.html",
        {"request": request, "user": user}
    )
