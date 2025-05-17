import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    response = client.post("/auth/token", data={"username": "Test", "password": "1111"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/token", data={"username": "Test", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/token", data={"username": "nonexistent", "password": "1111"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(client):
    response = client.post(
        "/auth/token", data={"username": "inactiveuser", "password": "1111"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expired_access_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer expired_token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_success(client):
    response = client.post("/auth/token", data={"username": "Test", "password": "1111"})
    assert response.status_code == 200
    refresh_token = response.json()["refresh_token"]
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    response = client.post("/auth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_success(client):
    response = client.post("/auth/token", data={"username": "Test", "password": "1111"})
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "Test"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_no_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
