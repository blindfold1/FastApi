from pydantic import BaseModel, Field , ConfigDict
from sqlalchemy import Column
from sqlalchemy.orm import declarative_base, DeclarativeBase , Mapped , mapped_column
from typing_extensions import Optional

class User_Schema(BaseModel):
    id : Optional[int] = None
    name : str
    weight : int
    height : int
    age : int
    username : str
    password : str

class User_Credentials(BaseModel):
    username : str
    password : str

class Updated_User_Schema(BaseModel):
    id : Optional[int] = None
    name : str
    weight : int
    height : int
    age : int
