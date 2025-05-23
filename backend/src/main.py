# backend/src/main.py
import os
from contextlib import asynccontextmanager
from pathlib import Path
import logging

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .db.database import database_router
from .api.routes import auth_router, articles_router
from .core import settings
from .core.config import logger
from .api.routes.blog import router as blog_router
from .db.mongodb import mongodb

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    await startup_db_client()
    yield
    logger.info("Shutting down application...")
    await shutdown_db_client()

app = FastAPI(
    title="Blog Platform API",
    description="API для платформы блогов",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "favicon": "/static/favicon.ico",
        "customJs": "/static/swagger-custom.js",
    },
    lifespan=lifespan,
    openapi_extra={
        "components": {
            "securitySchemes": {
                "AccessToken": {
                    "type": "oauth2",
                    "flows": {
                        "password": {
                            "scopes": {
                                "user": "Access as a regular user",
                                "admin": "Access as an admin user",
                            },
                            "tokenUrl": "/auth/token",
                        }
                    },
                },
                "RefreshToken": {
                    "type": "oauth2",
                    "flows": {
                        "password": {
                            "scopes": {
                                "user": "Access as a regular user",
                                "admin": "Access as an admin user",
                            },
                            "tokenUrl": "/auth/refresh",
                        }
                    },
                },
            }
        }
    },
)

# Настраиваем статические файлы
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Подключаем основные роутеры
app.include_router(database_router)
app.include_router(auth_router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(articles_router, prefix=settings.API_V1_STR, tags=["Articles"])

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем обработку ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.on_event("startup")
async def startup_db_client():
    """Подключение к MongoDB Atlas при запуске приложения"""
    await mongodb.connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown_db_client():
    """Закрытие подключения к MongoDB Atlas при остановке приложения"""
    await mongodb.close_mongodb_connection()

@app.get("/")
async def root():
    return {"message": "Welcome to Blog Platform API"}
