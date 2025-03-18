from typing import Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, select, Column
from src.db.database import Base

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    weight: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    age: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    scopes: Mapped[str] = mapped_column(String(255), default="me")




    @classmethod
    async def authenticate(cls, db, username: str, password: str):
        from src.core.security import AuthHandler  # Ленивый импорт
        user = await cls.get_by_username(db, username)
        if not user:
            return None
        if not AuthHandler().verify_password(password, user.password_hash):
            return None
        return user

    @classmethod
    async def get_by_username(cls, db, username: str):
        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalars().first()