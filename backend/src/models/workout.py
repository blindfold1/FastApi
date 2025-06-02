from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        schema.update(type="string")
        return schema

class WorkoutExercise(BaseModel):
    exercise_id: str
    name: str
    sets: int
    reps: int
    weight: Optional[float] = None
    notes: Optional[str] = None

class WorkoutBase(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    title: str
    exercises: List[WorkoutExercise]
    duration: Optional[int] = None  # in minutes
    notes: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutInDB(WorkoutBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class WorkoutResponse(WorkoutBase):
    id: str
    user_id: str 