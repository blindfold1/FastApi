from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, Optional

class BlogSerializer:
    @staticmethod
    def serialize_article(article: Dict[str, Any]) -> Dict[str, Any]:
        """Сериализация статьи для API"""
        return {
            "id": str(article["_id"]),
            "title": article["title"],
            "slug": article["slug"],
            "content": article["content"],
            "author_username": article["author_username"],
            "tags": article["tags"],
            "category": article["category"],
            "views": article["views"],
            "likes": article["likes"],
            "is_published": article["is_published"],
            "created_at": article["created_at"].isoformat() if isinstance(article["created_at"], datetime) else article["created_at"],
            "updated_at": article["updated_at"].isoformat() if isinstance(article["updated_at"], datetime) else article["updated_at"]
        }

    @staticmethod
    def serialize_comment(comment: Dict[str, Any]) -> Dict[str, Any]:
        """Сериализация комментария для API"""
        return {
            "id": str(comment["_id"]),
            "content": comment["content"],
            "author_username": comment["author_username"],
            "created_at": comment["created_at"].isoformat() if isinstance(comment["created_at"], datetime) else comment["created_at"]
        }

    @staticmethod
    def serialize_user(user: Dict[str, Any]) -> Dict[str, Any]:
        """Сериализация пользователя для API"""
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "is_admin": user["is_admin"],
            "created_at": user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else user["created_at"]
        }

    @staticmethod
    def deserialize_article_create(data: Dict[str, Any], author_id: ObjectId, author_username: str) -> Dict[str, Any]:
        """Десериализация данных для создания статьи"""
        return {
            "title": data["title"],
            "content": data["content"],
            "tags": data.get("tags", []),
            "category": data["category"],
            "author_id": author_id,
            "author_username": author_username,
            "views": 0,
            "likes": 0,
            "is_published": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    @staticmethod
    def deserialize_comment_create(data: Dict[str, Any], article_id: ObjectId, author_id: ObjectId, author_username: str) -> Dict[str, Any]:
        """Десериализация данных для создания комментария"""
        return {
            "content": data["content"],
            "article_id": article_id,
            "author_id": author_id,
            "author_username": author_username,
            "created_at": datetime.utcnow()
        } 