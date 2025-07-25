from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_303_SEE_OTHER
from werkzeug.security import generate_password_hash
import os
from app.database.crud.web.registration import user_exists, save_user

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# @router.get("/login", response_class=HTMLResponse)
# async def login_get(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})
#
#
# @router.post("/login", response_class=HTMLResponse)
# async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
#     print(f"Логін: {username}, Пароль: {password}")
#     return templates.TemplateResponse("home.html", {"request": request})
#
#
# @router.get("/register", response_class=HTMLResponse)
# async def register_get(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})


# @router.post("/register", response_class=HTMLResponse)
# async def register_post(
#         request: Request,
#         username: str = Form(...),
#         password: str = Form(...),
#         password_confirm: str = Form(...),
#         email: str = Form(...)
# ):
#     if password != password_confirm:
#         return templates.TemplateResponse("register.html", {"request": request, "error": "Паролі не співпадають!"})
#
#     if user_exists(username):
#         return templates.TemplateResponse("register.html", {"request": request, "error": "Такий логін вже існує!"})
#
#     password_hash = generate_password_hash(password)
#     print(f"Логін: {username}, Пароль: {password}, Пошта: {email}")
#     save_user(username, email, password_hash)
#
#     return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
