# tests/test_clients.py
import pytest


@pytest.mark.asyncio
async def test_create_user_success(client):
    response = client.post(  # Убрали await
        "/users",
        json={
            "username": "newuser",
            "password": "newpass",
            "name": "New User",
            "weight": 80,
            "height": 180,
            "age": 25,
            "fitness_goal": "gain",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["name"] == "New User"
    assert data["weight"] == 80
    assert data["height"] == 180
    assert data["age"] == 25
    assert data["fitness_goal"] == "gain"


# tests/test_clients.py
@pytest.mark.asyncio
async def test_create_user_duplicate_username(client, test_db):
    user_data = {
        "username": "duplicateuser",
        "password": "testpass",
        "name": "Duplicate User",
        "weight": 70.0,
        "height": 175.0,
        "age": 30,
        "fitness_goal": "maintain",
    }
    response = client.post("/users", json=user_data)
    response = client.post("/users", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"
