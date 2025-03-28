# backend/src/models/tables.py
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from backend.src.db.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    weight = Column(Float)
    height = Column(Float)
    age = Column(Integer)
    fitness_goal = Column(String)
    is_active = Column(Boolean, default=True)

    foods = relationship("Foods", back_populates="user")

    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str):
        from sqlalchemy import select
        from backend.src.core.security import (
            auth_handler,
        )  # Импорт перемещен внутрь метода

        query = select(Users).where(Users.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user and auth_handler.verify_password(password, user.password_hash):
            return user
        return None

    @staticmethod
    async def get_by_token(db: AsyncSession, token: str):
        from backend.src.core.security import (
            auth_handler,
        )  # Импорт перемещен внутрь метода

        username = auth_handler.decode_token(token)
        if not username:
            return None
        query = select(Users).where(Users.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str):
        from sqlalchemy import select

        query = select(Users).where(Users.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()


class Foods(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    calories = Column(Integer, nullable=False)
    carbs = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    proteins = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("Users", back_populates="foods")

    @staticmethod
    async def get_by_username(db: AsyncSession, name: str, user_id: int):
        from sqlalchemy import select

        query = select(Foods).where(Foods.name == name, Foods.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
