import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)

from src.main import app
from src.db.database import get_db
from src.db.base import Base
from src.models.tables import Users

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:3103@localhost:5432/users"
test_engine = create_async_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession)

app.dependency_overrides[get_db] = lambda: TestingSessionLocal()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto"
        )  # Используем тот же контекст
        hashed_password = pwd_context.hash("1111")  # Хешируем пароль как в /register
        test_user = Users(
            username="Test", password_hash=hashed_password, is_active=True
        )
        session.add(test_user)
        await session.commit()
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
