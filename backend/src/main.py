# backend/src/main.py
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .api.routes.tracker import tracker_router
from .db.database import engine, database_router
from .api.routes import auth_router, clients_router, food_router
from .core import settings
from .core.config import logger

RUNNING_TESTS = os.getenv("RUNNING_TESTS", "false").lower() == "true"

# Создаём фабрику сессий
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title="MyApi",
    description="GymHelper",
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


BASE_DIR = (
    Path(__file__).resolve().parent.parent.parent
)  # Поднимаемся на три уровня выше: backend/src -> gymhepler
STATIC_DIR = BASE_DIR / "static"

# Монтируем директорию static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# Подключаем маршруты напрямую
app.include_router(auth_router)
app.include_router(clients_router)

app.include_router(food_router)

app.include_router(tracker_router)

origins = [
    "http://localhost:5173",
    "http://localhost:80",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


app.include_router(database_router)
logger.info("Auth router included with routes: %s", database_router.routes)
app.include_router(auth_router)
logger.info("Auth router included with routes: %s", auth_router.routes)
app.include_router(clients_router)
logger.info("Clients router included with routes: %s", clients_router.routes)

app.include_router(food_router)
logger.info("Food router included with routes: %s", food_router.routes)
