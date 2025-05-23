# backend/src/db/database.py
import logging
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

logger = logging.getLogger(__name__)

# Инициализация клиента MongoDB
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]

# Collections
users_collection = db.users
articles_collection = db.articles
comments_collection = db.comments
likes_collection = db.likes

async def get_db():
    """Получение экземпляра базы данных"""
    return db

database_router = APIRouter()

@database_router.on_event("startup")
async def startup_db_client():
    try:
        # Verify the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

@database_router.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("MongoDB connection closed")
