from fastapi import APIRouter, Depends, HTTPException
from src.core.security import auth_handler
from src.db.mongo import MongoDB
from src.custom_serializer.formats.json_serializer import JsonSerializer
from datetime import date

router = APIRouter(tags=["Tracker"])
mongo = MongoDB()
serializer = JsonSerializer()

@router.post("/tracker/add-food")
async def add_food_to_tracker(food_id: str, current_user=Depends(auth_handler.get_current_user)):
    # Добавь метод get_food_by_id в MongoDB
    food = await mongo.get_food_by_id(food_id, current_user.id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    today = date.today().isoformat()
    tracker = await mongo.get_tracker(current_user.id, today)
    if not tracker:
        tracker = {"user_id": current_user.id, "date": today, "calories": 0, "foods": []}
    tracker["calories"] += food.get("calories", 0)
    tracker["foods"].append({"food_id": food_id, "name": food["name"]})

    tracker_id = await mongo.save_tracker(tracker)
    serializer.save_to_file(tracker, f"logs/tracker_{current_user.id}_{today}.txt")
    return {"id": tracker_id, **tracker}

# Добавь в класс MongoDB в mongo.py
async def get_food_by_id(self, food_id, user_id):
    return await self.db.foods.find_one({"_id": food_id, "user_id": user_id})