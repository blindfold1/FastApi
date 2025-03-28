from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from uvicorn import lifespan

from backend.src.api.routes import router
from backend.src.core import settings
from backend.src.core.config import logger
from backend.src.db.database import database_router, Base
from backend.src.db.dependencies import engine

@asynccontextmanager
async def lifespan(app : FastAPI):
    logger.info("Starting up application...")
    yield
    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Database connection closed")

app = FastAPI(
    title = "MyApi",
    description= "GymHelper",
    docs_url = "/docs",
    openapi_url = "/openapi.json",
    swagger_ui_parameters={
        "favicon":"/static/favicon.ico",

    },
    lifespan = lifespan
)
#я тебя люблю и я тебя люблю сииииииильно :)
app.include_router(router)
app.include_router(database_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

origin = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



