from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    ForeignKey,
    select,
    Date,
    DateTime,
)
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from ..core.config import logger
from ..core.security import auth_handler
from ..db.database import Base


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
    scope = Column(String(255), default="user", nullable=False)

    foods = relationship("Foods", back_populates="user", cascade="all, delete-orphan")
    tracker = relationship(
        "Tracker", back_populates="user", cascade="all, delete-orphan"
    )

    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str):
        logger.info(f"Authenticating user: {username}")
        query = select(Users).where(Users.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user:
            logger.info(f"User {username} found, verifying password...")
            if auth_handler.verify_password(password, user.password_hash):
                logger.info(f"User {username} authenticated successfully")
                return user
            else:
                logger.warning(f"Password verification failed for user {username}")
                return None
        logger.warning(f"User {username} not found")
        return None

    @staticmethod
    async def get_by_token(db: AsyncSession, token: str):
        logger.info("Decoding token to get username")
        username = auth_handler.decode_token(token)
        if not username:
            logger.error("Failed to decode token")
            return None
        logger.info(f"Token decoded, username: {username}")
        query = select(Users).where(Users.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user:
            logger.info(f"User {username} found by token")
        else:
            logger.warning(f"User {username} not found by token")
        return user

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str):
        logger.info(f"Querying user by username: {username}")
        query = select(Users).where(Users.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user:
            logger.info(f"User {username} found")
        else:
            logger.warning(f"User {username} not found")
        return user


class Foods(Base):
    __tablename__ = "foods"
    __table_args__ = {"extend_existing": True}  # Добавляем для предотвращения конфликта

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fats = Column(Float, nullable=False)
    proteins = Column(Float, nullable=False)
    vitamin_c = Column(Float, nullable=True)
    calcium = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("Users", back_populates="foods")

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str, user_id: int):
        logger.info(f"Querying food by name: {name} for user_id: {user_id}")
        query = select(Foods).where(Foods.name == name, Foods.user_id == user_id)
        result = await db.execute(query)
        food = result.scalar_one_or_none()
        if food:
            logger.info(f"Food {name} found for user_id: {user_id}")
        else:
            logger.info(f"Food {name} not found for user_id: {user_id}")
        return food


class Tracker(Base):
    __tablename__ = "tracker"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    calories = Column(Float, nullable=False, default=0.0)
    carbs = Column(Float, nullable=False, default=0.0)
    fats = Column(Float, nullable=False, default=0.0)
    proteins = Column(Float, nullable=False, default=0.0)

    user = relationship("Users", back_populates="tracker")

    @staticmethod
    async def get_by_user_and_date(db: AsyncSession, user_id: int, date: date):
        logger.info(f"Querying tracker for user_id: {user_id} on date: {date}")
        query = select(Tracker).where(Tracker.user_id == user_id, Tracker.date == date)
        result = await db.execute(query)
        tracker = result.scalar_one_or_none()
        if tracker:
            logger.info(f"Tracker found for user_id: {user_id} on date: {date}")
        else:
            logger.info(f"Tracker not found for user_id: {user_id} on date: {date}")
        return tracker
