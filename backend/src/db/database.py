from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, HTTPException
from backend.src.core.config import settings

import logging
import traceback

from backend.src.db.dependencies import SessionDep, AsyncSessionLocal

# Настройка базового класса для моделей
Base = declarative_base()

# Создание асинхронного движка
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)




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
        raise HTTPException(
            status_code=500,
            detail="Database creation failed"

        )

async def get_db() -> AsyncGenerator[Any, Any]:
    async with AsyncSessionLocal() as session:
        yield session