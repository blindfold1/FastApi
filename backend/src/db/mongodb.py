from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]

async def get_database():
    return db

async def connect_to_mongodb(self):
    """Подключение к MongoDB Atlas"""
    try:
        # Проверяем подключение
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {e}")
        raise

async def close_mongodb_connection(self):
    """Закрытие подключения к MongoDB Atlas"""
    if client:
        client.close()
        logger.info("MongoDB Atlas connection closed") 