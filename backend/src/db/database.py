# backend/src/db/database.py
import logging
import traceback
from typing import Any, AsyncGenerator

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from .base import Base
from .dependencies import engine
from ..core.config import settings

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True
)

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[Any, Any]:
    async with async_session() as session:
        yield session


database_router = APIRouter()


@database_router.post("/db")
async def setup_database():
    """Создание всех таблиц в базе данных"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return {"status": "Database tables created successfully"}
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database creation failed")
