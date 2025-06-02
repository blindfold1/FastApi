from ..models.workout import WorkoutCreate, WorkoutInDB, WorkoutResponse
from ..db.mongodb import get_database
from fastapi import HTTPException
from bson import ObjectId

class WorkoutService:
    @staticmethod
    async def create_workout(workout: WorkoutCreate, user_id: str) -> WorkoutResponse:
        db = await get_database()
        workout_dict = workout.dict()
        workout_dict["user_id"] = user_id
        result = await db.workouts.insert_one(workout_dict)
        created = await db.workouts.find_one({"_id": result.inserted_id})
        return WorkoutResponse(id=str(created["_id"]), user_id=created["user_id"], **{k: v for k, v in created.items() if k not in ["_id", "user_id"]})

    @staticmethod
    async def get_workout(workout_id: str) -> WorkoutResponse:
        db = await get_database()
        w = await db.workouts.find_one({"_id": ObjectId(workout_id)})
        if not w:
            raise HTTPException(status_code=404, detail="Workout not found")
        return WorkoutResponse(id=str(w["_id"]), user_id=w["user_id"], **{k: v for k, v in w.items() if k not in ["_id", "user_id"]})

    @staticmethod
    async def get_workouts(user_id: str, skip: int = 0, limit: int = 100):
        db = await get_database()
        workouts = await db.workouts.find({"user_id": user_id}).sort("date", -1).skip(skip).limit(limit).to_list(length=limit)
        return [WorkoutResponse(id=str(w["_id"]), user_id=w["user_id"], **{k: v for k, v in w.items() if k not in ["_id", "user_id"]}) for w in workouts]

    @staticmethod
    async def update_workout(workout_id: str, workout: WorkoutCreate, user_id: str):
        db = await get_database()
        w = await db.workouts.find_one({"_id": ObjectId(workout_id)})
        if not w:
            raise HTTPException(status_code=404, detail="Workout not found")
        if w["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this workout")
        await db.workouts.update_one({"_id": ObjectId(workout_id)}, {"$set": workout.dict()})
        updated = await db.workouts.find_one({"_id": ObjectId(workout_id)})
        return WorkoutResponse(id=str(updated["_id"]), user_id=updated["user_id"], **{k: v for k, v in updated.items() if k not in ["_id", "user_id"]})

    @staticmethod
    async def delete_workout(workout_id: str, user_id: str):
        db = await get_database()
        w = await db.workouts.find_one({"_id": ObjectId(workout_id)})
        if not w:
            raise HTTPException(status_code=404, detail="Workout not found")
        if w["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this workout")
        await db.workouts.delete_one({"_id": ObjectId(workout_id)})
        return {"message": "Workout deleted"} 