import secrets
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from app.web.routes import router
from starlette.middleware.sessions import SessionMiddleware
import os
from app.database.core.paths import STATIC_DIR


def create_app() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    # Додаємо SessionMiddleware
    application.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Дозволити запити з будь-яких доменів
        allow_credentials=True,  # Дозволити передавати куки, токени
        allow_methods=["*"],  # Дозволити всі HTTP методи (GET, POST, PUT, DELETE)
        allow_headers=["*"],  # Дозволити всі заголовки в запитах
    )
    # Шлях до статичної папки
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return application


app = create_app()


def run_fastapi():
    import uvicorn
    # Підключаємо папку зі статичними файлами
    uvicorn.run("app.web.start_web:app", host="0.0.0.0", port=5000, reload=True)
