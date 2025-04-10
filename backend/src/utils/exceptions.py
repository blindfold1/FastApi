# backend/src/utils/exceptions.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import logger


async def handle_db_error(
    db: AsyncSession, e: Exception, message: str = "Внутренняя ошибка сервера"
):
    """
    Обработчик ошибок базы данных.

    Args:
        db: Сессия базы данных.
        e: Исключение.
        message: Сообщение об ошибке для клиента.
    """
    await db.rollback()
    logger.error(f"Database error: {str(e)}")
    raise HTTPException(status_code=500, detail=message)


async def handle_generic_error(
    db: AsyncSession, e: Exception, message: str = "Внутренняя ошибка сервера"
):
    """
    Обработчик общих ошибок.

    Args:
        db: Сессия базы данных.
        e: Исключение.
        message: Сообщение об ошибке для клиента.
    """
    await db.rollback()
    logger.error(f"General error: {str(e)}")
    raise HTTPException(status_code=500, detail=message)
