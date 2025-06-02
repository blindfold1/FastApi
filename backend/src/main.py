# backend/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .core import settings
from .api.routes.user import router as user_router
from .api.routes.post import router as post_router
from .api.routes.exercise import router as exercise_router
from .api.routes.workout import router as workout_router

app = FastAPI(
    title="Fitness Platform API",
    description="API для платформы пользователей, тренеров и админов",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(user_router, prefix=settings.API_V1_STR)
app.include_router(post_router, prefix=settings.API_V1_STR)
app.include_router(exercise_router, prefix=settings.API_V1_STR)
app.include_router(workout_router, prefix=settings.API_V1_STR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Fitness Platform API"}
