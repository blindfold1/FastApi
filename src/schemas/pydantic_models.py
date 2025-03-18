from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    name: str
    weight: int
    height: int
    age: int
    username: str



class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    age: Optional[int] = None
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
