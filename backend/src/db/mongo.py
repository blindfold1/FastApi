from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings

class MongoDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client.gymhelper

    async def save_food(self, food_data):
        result = await self.db.foods.insert_one(food_data)
        return str(result.inserted_id)

    async def get_food(self, name, user_id):
        return await self.db.foods.find_one({"name": name, "user_id": user_id})

    async def save_tracker(self, tracker_data):
        result = await self.db.trackers.insert_one(tracker_data)
        return str(result.inserted_id)

    async def get_tracker(self, user_id, date):
        return await self.db.trackers.find_one({"user_id": user_id, "date": date})

    async def save_user(self, user_data):
        result = await self.db.users.insert_one(user_data)
        return str(result.inserted_id)

    async def get_user(self, user_id):
        return await self.db.users.find_one({"id": user_id})