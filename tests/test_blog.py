import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Тестовые данные
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
}

TEST_ARTICLE = {
    "title": "Test Article",
    "content": "This is a test article content",
    "category": "Technology",
    "tags": ["test", "python"]
}

TEST_COMMENT = {
    "content": "This is a test comment"
}

@pytest.fixture
def client():
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

@pytest.mark.asyncio
async def test_create_article(client, test_db):
    # Сначала создаем пользователя
    response = client.post("/api/auth/register", json=TEST_USER)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Создаем статью
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/articles/", json=TEST_ARTICLE, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == TEST_ARTICLE["title"]
    assert data["content"] == TEST_ARTICLE["content"]

@pytest.mark.asyncio
async def test_get_articles(client, test_db):
    response = client.get("/api/articles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_article_by_slug(client, test_db):
    # Создаем пользователя и статью
    response = client.post("/api/auth/register", json=TEST_USER)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    article_response = client.post("/api/articles/", json=TEST_ARTICLE, headers=headers)
    article_slug = article_response.json()["slug"]
    
    # Получаем статью по slug
    response = client.get(f"/api/articles/{article_slug}")
    assert response.status_code == 200
    assert response.json()["slug"] == article_slug

@pytest.mark.asyncio
async def test_create_comment(client, test_db):
    # Создаем пользователя и статью
    response = client.post("/api/auth/register", json=TEST_USER)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    article_response = client.post("/api/articles/", json=TEST_ARTICLE, headers=headers)
    article_slug = article_response.json()["slug"]
    
    # Создаем комментарий
    response = client.post(
        f"/api/articles/{article_slug}/comments",
        json=TEST_COMMENT,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["content"] == TEST_COMMENT["content"]

@pytest.mark.asyncio
async def test_like_article(client, test_db):
    # Создаем пользователя и статью
    response = client.post("/api/auth/register", json=TEST_USER)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    article_response = client.post("/api/articles/", json=TEST_ARTICLE, headers=headers)
    article_slug = article_response.json()["slug"]
    
    # Ставим лайк
    response = client.post(f"/api/articles/{article_slug}/like", headers=headers)
    assert response.status_code == 200
    
    # Проверяем, что лайк добавлен
    article = client.get(f"/api/articles/{article_slug}")
    assert article.json()["likes_count"] == 1

@pytest.mark.asyncio
async def test_search_articles(client, test_db):
    # Создаем пользователя и статью
    response = client.post("/api/auth/register", json=TEST_USER)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    client.post("/api/articles/", json=TEST_ARTICLE, headers=headers)
    
    # Ищем статью
    response = client.get("/api/articles/search?query=test")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_categories(client, test_db):
    response = client.get("/api/articles/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_tags(client, test_db):
    response = client.get("/api/articles/tags")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 