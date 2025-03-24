from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, select

from backend.src.core.config import logger
from backend.src.db.database import Base

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


    async def authenticate(db: AsyncSession, username: str, password: str):
        from backend.src.core.security import AuthHandler
        user = await Users.get_by_username(db, username)
        if not user:
            return None
        if not AuthHandler().verify_password(password, user.password_hash):
            return None
        return user


    async def get_by_username(db: AsyncSession, username: str):
        result = await db.execute(select(Users).where(Users.username == username))
        user = result.scalars().first()
        if user is None:
            logger.warning(f"Пользователь {username} не найден")
        return user