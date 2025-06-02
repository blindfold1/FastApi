import pytest
from fastapi.testclient import TestClient
from ..src.main import app
from ..src.core.security import auth_handler

client = TestClient(app)

def test_create_exercise():
    # Создаем тестового пользователя-тренера
    trainer_data = {
        "username": "test_trainer",
        "email": "trainer@test.com",
        "password": "testpass123",
        "role": "trainer"
    }
    response = client.post("/api/v1/users/", json=trainer_data)
    assert response.status_code == 200
    trainer = response.json()
    
    # Получаем токен
    login_data = {
        "username": "test_trainer",
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Создаем упражнение
    exercise_data = {
        "name": "Test Exercise",
        "description": "Test Description",
        "type": "strength",
        "target_muscles": ["chest", "triceps"],
        "equipment": "barbell",
        "image_url": None,
        "video_url": None
    }
    response = client.post(
        "/api/v1/exercises/",
        json=exercise_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    exercise = response.json()
    assert exercise["name"] == exercise_data["name"]
    assert exercise["type"] == exercise_data["type"]

def test_get_exercises():
    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    exercises = response.json()
    assert isinstance(exercises, list)
    assert len(exercises) > 0

def test_get_exercise():
    # Сначала получаем список упражнений
    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) > 0
    
    # Получаем конкретное упражнение
    exercise_id = exercises[0]["id"]
    response = client.get(f"/api/v1/exercises/{exercise_id}")
    assert response.status_code == 200
    exercise = response.json()
    assert exercise["id"] == exercise_id

def test_update_exercise():
    # Создаем тестового пользователя-тренера
    trainer_data = {
        "username": "test_trainer2",
        "email": "trainer2@test.com",
        "password": "testpass123",
        "role": "trainer"
    }
    response = client.post("/api/v1/users/", json=trainer_data)
    assert response.status_code == 200
    
    # Получаем токен
    login_data = {
        "username": "test_trainer2",
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Получаем ID упражнения
    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) > 0
    exercise_id = exercises[0]["id"]
    
    # Обновляем упражнение
    update_data = {
        "name": "Updated Exercise",
        "description": "Updated Description",
        "type": "strength",
        "target_muscles": ["chest", "triceps"],
        "equipment": "dumbbell",
        "image_url": None,
        "video_url": None
    }
    response = client.put(
        f"/api/v1/exercises/{exercise_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == update_data["name"]
    assert updated["description"] == update_data["description"]

def test_delete_exercise():
    # Создаем тестового пользователя-админа
    admin_data = {
        "username": "test_admin",
        "email": "admin@test.com",
        "password": "testpass123",
        "role": "admin"
    }
    response = client.post("/api/v1/users/", json=admin_data)
    assert response.status_code == 200
    
    # Получаем токен
    login_data = {
        "username": "test_admin",
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Получаем ID упражнения
    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) > 0
    exercise_id = exercises[0]["id"]
    
    # Удаляем упражнение
    response = client.delete(
        f"/api/v1/exercises/{exercise_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Проверяем, что упражнение удалено
    response = client.get(f"/api/v1/exercises/{exercise_id}")
    assert response.status_code == 404 