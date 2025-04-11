from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: Optional[str] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    age: Optional[int] = None
    username: Optional[str] = None
    fitness_goal: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)




class UserUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    age: Optional[int] = None
    username: Optional[str] = None
    fitness_goal: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TrackerBase(BaseModel):
    user_id: int
    date: date
    calories: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    fats: Optional[float] = 0.0
    proteins: Optional[float] = 0.0

class TrackerCreate(TrackerBase):
    pass

class TrackerUpdate(BaseModel):
    calories: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None
    proteins: Optional[float] = None


class TrackerResponse(TrackerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class FoodBase(BaseModel):
    id: int
    name: str
    calories: float
    proteins: float  # Change from int to float
    fats: float
    carbs: float  # Change from int to float
    vitamin_c: float
    calcium: float

class FoodCreate(FoodBase):
    pass

# backend/src/schemas/pydantic_models.py
from pydantic import BaseModel

class FoodResponse(BaseModel):
    id: int
    name: str
    calories: float
    proteins: float
    fats: float
    carbs: float
    vitamin_c: float
    calcium: float
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


