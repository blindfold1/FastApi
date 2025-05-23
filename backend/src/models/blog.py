from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_cache) -> dict:
        return {"type": "string"}

# Базовые модели для создания
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []
    category: str

class CommentCreate(BaseModel):
    content: str

# Полные модели данных
class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class Article(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    slug: str
    content: str
    author_id: PyObjectId
    author_username: str
    tags: List[str] = []
    category: str
    views: int = 0
    likes: int = 0
    is_published: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class Comment(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    article_id: PyObjectId
    author_id: PyObjectId
    author_username: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

# Модели ответов
class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime
    is_admin: bool

class ArticleResponse(BaseModel):
    id: str
    title: str
    slug: str
    content: str
    author_username: str
    tags: List[str]
    category: str
    views: int
    likes: int
    created_at: datetime
    updated_at: datetime

class CommentResponse(BaseModel):
    id: str
    content: str
    author_username: str
    created_at: datetime

# Модели для токенов
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer" 