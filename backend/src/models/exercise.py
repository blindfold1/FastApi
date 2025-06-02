from pydantic import BaseModel, Field
from typing import List, Optional
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

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str  # strength, cardio, mobility, etc.
    target_muscles: List[str] = []
    equipment: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseInDB(ExerciseBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_by: Optional[str] = None  # username or id
    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class ExerciseResponse(ExerciseBase):
    id: str
    created_by: Optional[str] = None 