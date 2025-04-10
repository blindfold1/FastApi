from typing import Optional

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
    id : int
    user_ud : int
    calories : Optional[int] = 0
    carbs : Optional[int] = 0
    fats : Optional[int] = 0
    proteins : Optional[int] = 0

class TrackerCreate(TrackerBase):
    pass

class TrackerUpdate(TrackerBase):
    user_ud : int
    calories: Optional[int] = 0
    carbs: Optional[int] = 0
    fats: Optional[int] = 0
    proteins: Optional[int] = 0

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
    proteins: float  # Change from int to float
    fats: float
    carbs: float     # Change from int to float
    vitamin_c: float
    calcium: float
    user_id: int     # Fix the typo: change user_ud to user_id

    class Config:
        from_attributes = True



