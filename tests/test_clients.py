import pytest


@pytest.mark.asyncio
async def test_create_user_success(client):
    response = client.post(
        "/users",
        json={
            "username": "newuser",
            "password": "1111",
            "name": "New User",
            "weight": 80.0,
            "height": 180.0,
            "age": 25,
            "fitness_goal": "gain",
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


@pytest.mark.asyncio
async def test_create_user_duplicate_username(client):
    response = client.post(
        "/users",
        json={
            "username": "Test",
            "password": "1111",
            "name": "Test User",
            "weight": 70.0,
            "height": 175.0,
            "age": 30,
            "fitness_goal": "maintain",
        },
    )
    response = client.post(
        "/users",
        json={
            "username": "Test",
            "password": "1111",
            "name": "Test User",
            "weight": 70.0,
            "height": 175.0,
            "age": 30,
            "fitness_goal": "maintain",
        },
    )
    assert response.status_code == 400
