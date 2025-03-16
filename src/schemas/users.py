from typing import Optional

from pydantic import BaseModel

class UserSchema(BaseModel):
    id: Optional[int] = None
    name: str
    weight: int
    height: int
    age: int
    username: str
    password: str

class UserCredentials(BaseModel):
    username: str
    password: str
