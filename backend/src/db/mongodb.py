from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongodb(self):
        """Подключение к MongoDB Atlas"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DB_NAME]
            # Проверяем подключение
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            raise

    async def close_mongodb_connection(self):
        """Закрытие подключения к MongoDB Atlas"""
        if self.client:
            self.client.close()
            logger.info("MongoDB Atlas connection closed")

mongodb = MongoDB()

async def get_database():
    """Получение экземпляра базы данных"""
    return mongodb.db 