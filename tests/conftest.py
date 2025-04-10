# tests/conftest.py
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pytest_httpx import HTTPXMock

# Добавляем путь к backend в sys.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)

from src.main import app
from src.db.database import get_db, engine
from src.db.base import Base
from src.models.tables import Users

# Создаём тестовую базу данных
TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/test_gymhepler"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession
)


# Переопределяем зависимость get_db для тестов
async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


# Создаём фикстуру для клиента
@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


# Создаём таблицы перед тестами и очищаем их после
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # Создаём таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создаём тестового пользователя
    async with TestingSessionLocal() as session:
        test_user = Users(
            username="testuser",
            email="testuser@example.com",
            hashed_password="testpassword",  # В реальном приложении нужно хешировать
            is_active=True,
        )
        session.add(test_user)
        await session.commit()

    yield

    # Очищаем таблицы после тестов
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Фикстура для мокинга HTTP-запросов
@pytest.fixture
def httpx_mock():
    with HTTPXMock() as mock:
        yield mock
