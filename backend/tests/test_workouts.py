import pytest
from fastapi.testclient import TestClient
from ..src.main import app
from ..src.core.security import auth_handler

client = TestClient(app)

def test_create_workout():
    # Создаем тестового пользователя
    user_data = {
        "username": "test_user",
        "email": "user@test.com",
        "password": "testpass123",
        "role": "user"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    # Получаем токен
    login_data = {
        "username": "test_user",
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Получаем список упражнений
    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) > 0
    
    # Создаем тренировку
    workout_data = {
        "title": "Test Workout",
        "date": "2024-03-20T10:00:00",
        "exercises": [
            {
                "exercise_id": exercises[0]["id"],
                "name": exercises[0]["name"],
                "sets": 3,
                "reps": 10,
                "weight": 20.5,
                "notes": "Test notes"
            }
        ],
        "duration": 45,
        "notes": "Test workout notes"
    }
    response = client.post(
        "/api/v1/workouts/",
        json=workout_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    workout = response.json()
    assert workout["title"] == workout_data["title"]
    assert len(workout["exercises"]) == 1

def test_get_workouts():
    # Создаем тестового пользователя
    user_data = {
        "username": "test_user2",
        "email": "user2@test.com",
        "password": "testpass123",
        "role": "user"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    # Получаем токен
    login_data = {
        "username": "test_user2",
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Получаем список тренировок
    response = client.get(
        "/api/v1/workouts/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    workouts = response.json()
    assert isinstance(workouts, list)

def test_get_workout():
    # Создаем тестового пользователя
    user_data = {
        "username": "test_user3",
        "email": "user3@test.com",
        "password": "testpass123",
        "role": "user"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    # Получаем токен
    login_data = {
        "username": "test_user3",
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Создаем тренировку
    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) > 0
    
    workout_data = {
        "title": "Test Workout 2",
        "date": "2024-03-20T11:00:00",
        "exercises": [
            {
                "exercise_id": exercises[0]["id"],
                "name": exercises[0]["name"],
                "sets": 3,
                "reps": 10,
                "weight": 20.5,
                "notes": "Test notes"
            }
        ],
        "duration": 45,
        "notes": "Test workout notes"
    }
    response = client.post(
        "/api/v1/workouts/",
        json=workout_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    workout = response.json()
    workout_id = workout["id"]
    
    # Получаем конкретную тренировку
    response = client.get(
        f"/api/v1/workouts/{workout_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    workout = response.json()
    assert workout["id"] == workout_id

def test_update_workout():
    # Создаем тестового пользователя
    user_data = {
        "username": "test_user4",
        "email": "user4@test.com",
        "password": "testpass123",
        "role": "user"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    # Получаем токен
    login_data = {
        "username": "test_user4",
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Создаем тренировку
    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) > 0
    
    workout_data = {
        "title": "Test Workout 3",
        "date": "2024-03-20T12:00:00",
        "exercises": [
            {
                "exercise_id": exercises[0]["id"],
                "name": exercises[0]["name"],
                "sets": 3,
                "reps": 10,
                "weight": 20.5,
                "notes": "Test notes"
            }
        ],
        "duration": 45,
        "notes": "Test workout notes"
    }
    response = client.post(
        "/api/v1/workouts/",
        json=workout_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    workout = response.json()
    workout_id = workout["id"]
    
    # Обновляем тренировку
    update_data = {
        "title": "Updated Workout",
        "date": "2024-03-20T13:00:00",
        "exercises": [
            {
                "exercise_id": exercises[0]["id"],
                "name": exercises[0]["name"],
                "sets": 4,
                "reps": 12,
                "weight": 22.5,
                "notes": "Updated notes"
            }
        ],
        "duration": 60,
        "notes": "Updated workout notes"
    }
    response = client.put(
        f"/api/v1/workouts/{workout_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == update_data["title"]
    assert updated["duration"] == update_data["duration"]

def test_delete_workout():
    # Создаем тестового пользователя
    user_data = {
        "username": "test_user5",
        "email": "user5@test.com",
        "password": "testpass123",
        "role": "user"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    # Получаем токен
    login_data = {
        "username": "test_user5",
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Создаем тренировку
    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) > 0
    
    workout_data = {
        "title": "Test Workout 4",
        "date": "2024-03-20T14:00:00",
        "exercises": [
            {
                "exercise_id": exercises[0]["id"],
                "name": exercises[0]["name"],
                "sets": 3,
                "reps": 10,
                "weight": 20.5,
                "notes": "Test notes"
            }
        ],
        "duration": 45,
        "notes": "Test workout notes"
    }
    response = client.post(
        "/api/v1/workouts/",
        json=workout_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    workout = response.json()
    workout_id = workout["id"]
    
    # Удаляем тренировку
    response = client.delete(
        f"/api/v1/workouts/{workout_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Проверяем, что тренировка удалена
    response = client.get(
        f"/api/v1/workouts/{workout_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404 