from ..models.exercise import ExerciseCreate, ExerciseInDB, ExerciseResponse
from ..db.mongodb import get_database
from fastapi import HTTPException
from bson import ObjectId

class ExerciseService:
    @staticmethod
    async def create_exercise(exercise: ExerciseCreate, created_by: str) -> ExerciseResponse:
        db = await get_database()
        exercise_dict = exercise.dict()
        exercise_dict["created_by"] = created_by
        result = await db.exercises.insert_one(exercise_dict)
        created = await db.exercises.find_one({"_id": result.inserted_id})
        return ExerciseResponse(id=str(created["_id"]), **{k: v for k, v in created.items() if k != "_id"})

    @staticmethod
    async def get_exercise(exercise_id: str) -> ExerciseResponse:
        db = await get_database()
        ex = await db.exercises.find_one({"_id": ObjectId(exercise_id)})
        if not ex:
            raise HTTPException(status_code=404, detail="Exercise not found")
        return ExerciseResponse(id=str(ex["_id"]), **{k: v for k, v in ex.items() if k != "_id"})

    @staticmethod
    async def get_exercises(skip: int = 0, limit: int = 100, search: str = None):
        db = await get_database()
        query = {}
        if search:
            query["name"] = {"$regex": search, "$options": "i"}
        exercises = await db.exercises.find(query).skip(skip).limit(limit).to_list(length=limit)
        return [ExerciseResponse(id=str(e["_id"]), **{k: v for k, v in e.items() if k != "_id"}) for e in exercises]

    @staticmethod
    async def update_exercise(exercise_id: str, exercise: ExerciseCreate):
        db = await get_database()
        await db.exercises.update_one({"_id": ObjectId(exercise_id)}, {"$set": exercise.dict()})
        updated = await db.exercises.find_one({"_id": ObjectId(exercise_id)})
        if not updated:
            raise HTTPException(status_code=404, detail="Exercise not found")
        return ExerciseResponse(id=str(updated["_id"]), **{k: v for k, v in updated.items() if k != "_id"})

    @staticmethod
    async def delete_exercise(exercise_id: str):
        db = await get_database()
        result = await db.exercises.delete_one({"_id": ObjectId(exercise_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Exercise not found")
        return {"message": "Exercise deleted"} 