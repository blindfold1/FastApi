import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

TEST_USER = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpass123"
}

TEST_POST = {
    "title": "Test Post",
    "content": "This is a test post content",
    "tags": ["test", "blog"],
    "is_published": True
}

TEST_COMMENT = {
    "content": "This is a test comment"
}

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function", autouse=True)
async def clear_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    await db.users.delete_many({})
    await db.posts.delete_many({})
    await db.comments.delete_many({})
    await db.likes.delete_many({})
    yield
    await db.users.delete_many({})
    await db.posts.delete_many({})
    await db.comments.delete_many({})
    await db.likes.delete_many({})
    client.close()

@pytest.mark.asyncio
async def test_register_and_login(client):
    # Регистрация
    response = client.post("/api/users/register", json=TEST_USER)
    assert response.status_code == 200
    # Логин
    response = client.post("/api/users/login", data={"username": TEST_USER["username"], "password": TEST_USER["password"]})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_create_post_and_feed(client):
    # Регистрация и логин
    client.post("/api/users/register", json=TEST_USER)
    login = client.post("/api/users/login", data={"username": TEST_USER["username"], "password": TEST_USER["password"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Создание поста
    response = client.post("/api/posts/", json=TEST_POST, headers=headers)
    assert response.status_code == 200
    post_id = response.json()["id"]
    # Лента
    feed = client.get("/api/posts/feed")
    assert feed.status_code == 200
    assert any(post["id"] == post_id for post in feed.json())

@pytest.mark.asyncio
async def test_comment_and_like(client):
    # Регистрация и логин
    client.post("/api/users/register", json=TEST_USER)
    login = client.post("/api/users/login", data={"username": TEST_USER["username"], "password": TEST_USER["password"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Создание поста
    post = client.post("/api/posts/", json=TEST_POST, headers=headers).json()
    post_id = post["id"]
    # Комментарий
    comment = client.post(f"/api/posts/{post_id}/comments", json=TEST_COMMENT, headers=headers)
    assert comment.status_code == 200
    assert comment.json()["content"] == TEST_COMMENT["content"]
    # Лайк
    like = client.post(f"/api/posts/{post_id}/like", headers=headers)
    assert like.status_code == 200
    # Проверка лайка
    post_data = client.get(f"/api/posts/{post_id}").json()
    assert post_data["likes_count"] == 1

@pytest.mark.asyncio
async def test_delete_post_and_comment(client):
    # Регистрация и логин
    client.post("/api/users/register", json=TEST_USER)
    login = client.post("/api/users/login", data={"username": TEST_USER["username"], "password": TEST_USER["password"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Создание поста
    post = client.post("/api/posts/", json=TEST_POST, headers=headers).json()
    post_id = post["id"]
    # Комментарий
    comment = client.post(f"/api/posts/{post_id}/comments", json=TEST_COMMENT, headers=headers).json()
    comment_id = comment["id"]
    # Удаление комментария
    del_comment = client.delete(f"/api/posts/comments/{comment_id}", headers=headers)
    assert del_comment.status_code == 200
    # Удаление поста
    del_post = client.delete(f"/api/posts/{post_id}", headers=headers)
    assert del_post.status_code == 200 