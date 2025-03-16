import logging
import asyncio
import traceback
import aiomysql
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import  DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.sql import text
from src.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from fastapi import APIRouter, HTTPException


class Base(DeclarativeBase):
    pass

engine = create_async_engine(DATABASE_URL,echo = True, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
logging.basicConfig(level=logging.DEBUG)
database_router = APIRouter()
# Создание базы данных
@database_router.post("/db")
async def setup_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            return {"Success": True}
    except SQLAlchemyError as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Something went wrong")
