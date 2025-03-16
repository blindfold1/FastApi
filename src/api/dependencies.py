from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Any, AsyncGenerator

from sqlalchemy.orm import sessionmaker

from src.models.database import async_session, engine

async_session = sessionmaker(
    bind = engine,class_=AsyncSession,expire_on_commit=False
)


async def get_database() -> AsyncGenerator[Any, Any]:
    async with async_session() as session:
        yield session


async def SessionDep() -> AsyncGenerator[Any, Any]:
    async with async_session() as session:
        yield session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
