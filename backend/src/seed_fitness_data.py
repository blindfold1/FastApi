import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "gymhepler"

EXERCISES = [
    {
        "name": "Push Up",
        "description": "A bodyweight exercise for chest, shoulders, and triceps.",
        "type": "strength",
        "target_muscles": ["chest", "triceps", "shoulders"],
        "equipment": None,
        "image_url": None,
        "video_url": None,
        "created_by": "admin"
    },
    {
        "name": "Squat",
        "description": "A lower body exercise targeting quads, glutes, and hamstrings.",
        "type": "strength",
        "target_muscles": ["quads", "glutes", "hamstrings"],
        "equipment": None,
        "image_url": None,
        "video_url": None,
        "created_by": "admin"
    },
    {
        "name": "Plank",
        "description": "An isometric core exercise.",
        "type": "core",
        "target_muscles": ["core"],
        "equipment": None,
        "image_url": None,
        "video_url": None,
        "created_by": "admin"
    },
]

WORKOUTS = [
    {
        "title": "Full Body Beginner",
        "date": datetime.utcnow(),
        "exercises": [
            {"exercise_id": None, "name": "Push Up", "sets": 3, "reps": 10, "weight": None, "notes": ""},
            {"exercise_id": None, "name": "Squat", "sets": 3, "reps": 15, "weight": None, "notes": ""},
            {"exercise_id": None, "name": "Plank", "sets": 3, "reps": 1, "weight": None, "notes": "30 sec each"},
        ],
        "duration": 30,
        "notes": "Great for beginners!",
        "user_id": None  # Заполнить после создания пользователя
    }
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Очистить коллекции
    await db.exercises.delete_many({})
    await db.workouts.delete_many({})

    # Добавить упражнения
    exercise_ids = []
    for ex in EXERCISES:
        result = await db.exercises.insert_one(ex)
        exercise_ids.append(result.inserted_id)
    print(f"Inserted exercises: {exercise_ids}")

    # Получить пользователя для user_id (например, первого пользователя)
    user = await db.users.find_one({})
    if not user:
        print("Нет пользователей в базе. Создайте пользователя через API.")
        return
    user_id = str(user["_id"])

    # Добавить тренировку с реальными exercise_id
    workout = WORKOUTS[0].copy()
    for i, ex in enumerate(workout["exercises"]):
        ex["exercise_id"] = str(exercise_ids[i])
    workout["user_id"] = user_id
    await db.workouts.insert_one(workout)
    print("Inserted workout for user:", user_id)

    client.close()

if __name__ == "__main__":
    asyncio.run(seed()) 