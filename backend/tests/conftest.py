import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from ..src.main import app
from ..src.core import settings

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    # Подключаемся к тестовой базе данных
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME + "_test"]
    
    # Очищаем базу перед тестами
    await db.users.delete_many({})
    await db.exercises.delete_many({})
    await db.workouts.delete_many({})
    
    yield db
    
    # Очищаем базу после тестов
    await db.users.delete_many({})
    await db.exercises.delete_many({})
    await db.workouts.delete_many({})
    client.close()

@pytest.fixture(scope="session")
def test_client():
    return app.test_client() 