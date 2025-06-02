from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
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

class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    image_url: Optional[str] = None
    is_published: bool = True

class PostCreate(PostBase):
    pass

class PostInDB(PostBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    author_id: PyObjectId
    author_username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    likes_count: int = 0
    comments_count: int = 0

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class PostResponse(PostBase):
    id: str
    author_id: str
    author_username: str
    created_at: datetime
    updated_at: datetime
    likes_count: int
    comments_count: int

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentInDB(CommentBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    post_id: PyObjectId
    author_id: PyObjectId
    author_username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class CommentResponse(CommentBase):
    id: str
    post_id: str
    author_id: str
    author_username: str
    created_at: datetime

class LikeInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    post_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True 