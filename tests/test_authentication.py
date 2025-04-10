import pytest
from datetime import datetime, timedelta
from jose import jwt
from src.core.config import settings
from src.core.security import auth_handler
from src.models.tables import Users
from conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = client.post(  # Убрали await
        "/auth/token",
        data={"username": "nonexistent", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect credentials"


# tests/test_authentication.py
@pytest.mark.asyncio
async def test_login_inactive_user(client, test_db):
    async with TestingSessionLocal() as session:
        hashed_password = auth_handler.get_password_hash("testpass")
        user = Users(
            username="inactiveuser",
            password_hash=hashed_password,
            name="Inactive User",
            weight=70.0,
            height=175.0,
            age=30,
            fitness_goal="maintain",
            is_active=False,
            scope="user",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    response = client.post(
        "/auth/token",
        data={"username": "inactiveuser", "password": "testpass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Inactive user"


@pytest.mark.asyncio
async def test_expired_access_token(client, test_user):
    expired_token = jwt.encode(
        {"sub": "testuser", "exp": datetime.utcnow() - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    response = client.get(  # Убрали await
        "/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_refresh_token_success(client, test_user):
    login_response = client.post(  # Убрали await
        "/auth/token",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(  # Убрали await
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    response = client.post(  # Убрали await
        "/auth/refresh", json={"refresh_token": "invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_get_current_user_success(client, test_user):
    login_response = client.post(  # Убрали await
        "/auth/token",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]

    response = client.get(  # Убрали await
        "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["name"] == "Test User"
    assert data["weight"] == 70.0
    assert data["height"] == 175.0
    assert data["age"] == 30
    assert data["fitness_goal"] == "maintain"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client):
    response = client.get(  # Убрали await
        "/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_get_current_user_no_token(client):
    response = client.get("/auth/me")  # Убрали await
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
