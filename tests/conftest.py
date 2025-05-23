import os
import sys
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from backend.src.main import app
from backend.src.core.config import settings

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def client():
    """Фикстура для тестового клиента"""
    return TestClient(app)

@pytest.fixture
async def test_db():
    """Фикстура для тестовой базы данных"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME + "_test"]
    
    # Очищаем тестовую базу перед каждым тестом
    await db.users.delete_many({})
    await db.articles.delete_many({})
    await db.comments.delete_many({})
    await db.likes.delete_many({})
    
    yield db
    
    # Очищаем тестовую базу после каждого теста
    await db.users.delete_many({})
    await db.articles.delete_many({})
    await db.comments.delete_many({})
    await db.likes.delete_many({})
    client.close()
