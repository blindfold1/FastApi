from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        schema.update(type="string")
        return schema

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "user"  # user, trainer, admin
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str
    # trainer-specific fields
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class UserResponse(UserBase):
    id: str
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None 