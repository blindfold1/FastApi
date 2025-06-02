from ..models.post import PostCreate, PostInDB, PostResponse, CommentCreate, CommentInDB, CommentResponse, LikeInDB
from ..models.user import PyObjectId
from ..db.mongodb import get_database
from fastapi import HTTPException, status
from bson import ObjectId, errors as bson_errors
from datetime import datetime

class PostService:
    @staticmethod
    async def create_post(post: PostCreate, author_id: str, author_username: str) -> PostResponse:
        db = await get_database()
        post_dict = post.dict()
        post_dict["author_id"] = ObjectId(author_id)
        post_dict["author_username"] = author_username
        post_dict["created_at"] = datetime.utcnow()
        post_dict["updated_at"] = datetime.utcnow()
        post_dict["likes_count"] = 0
        post_dict["comments_count"] = 0
        result = await db.posts.insert_one(post_dict)
        created_post = await db.posts.find_one({"_id": result.inserted_id})
        return PostResponse(
            id=str(created_post["_id"]),
            author_id=str(created_post["author_id"]),
            author_username=created_post["author_username"],
            title=created_post["title"],
            content=created_post["content"],
            tags=created_post.get("tags", []),
            image_url=created_post.get("image_url"),
            is_published=created_post.get("is_published", True),
            created_at=created_post["created_at"],
            updated_at=created_post["updated_at"],
            likes_count=created_post.get("likes_count", 0),
            comments_count=created_post.get("comments_count", 0),
        )

    @staticmethod
    async def get_post(post_id: str) -> PostResponse:
        db = await get_database()
        post = await db.posts.find_one({"_id": PostService.validate_object_id(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return PostResponse(
            id=str(post["_id"]),
            author_id=str(post["author_id"]),
            author_username=post["author_username"],
            title=post["title"],
            content=post["content"],
            tags=post.get("tags", []),
            image_url=post.get("image_url"),
            is_published=post.get("is_published", True),
            created_at=post["created_at"],
            updated_at=post["updated_at"],
            likes_count=post.get("likes_count", 0),
            comments_count=post.get("comments_count", 0),
        )

    @staticmethod
    async def get_posts(skip: int = 0, limit: int = 10, search: str = None, tag: str = None):
        db = await get_database()
        query = {"is_published": True}
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"content": {"$regex": search, "$options": "i"}}
            ]
        if tag:
            query["tags"] = tag
        posts = await db.posts.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        return [PostResponse(
            id=str(post["_id"]),
            author_id=str(post["author_id"]),
            author_username=post["author_username"],
            title=post["title"],
            content=post["content"],
            tags=post.get("tags", []),
            image_url=post.get("image_url"),
            is_published=post.get("is_published", True),
            created_at=post["created_at"],
            updated_at=post["updated_at"],
            likes_count=post.get("likes_count", 0),
            comments_count=post.get("comments_count", 0),
        ) for post in posts]

    @staticmethod
    async def update_post(post_id: str, post_update: PostCreate, current_user_id: str, is_admin: bool) -> PostResponse:
        db = await get_database()
        post = await db.posts.find_one({"_id": PostService.validate_object_id(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if str(post["author_id"]) != current_user_id and not is_admin:
            raise HTTPException(status_code=403, detail="Not authorized to update this post")
        update_data = post_update.dict()
        update_data["updated_at"] = datetime.utcnow()
        await db.posts.update_one({"_id": PostService.validate_object_id(post_id)}, {"$set": update_data})
        updated_post = await db.posts.find_one({"_id": PostService.validate_object_id(post_id)})
        return PostResponse(
            id=str(updated_post["_id"]),
            author_id=str(updated_post["author_id"]),
            author_username=updated_post["author_username"],
            title=updated_post["title"],
            content=updated_post["content"],
            tags=updated_post.get("tags", []),
            image_url=updated_post.get("image_url"),
            is_published=updated_post.get("is_published", True),
            created_at=updated_post["created_at"],
            updated_at=updated_post["updated_at"],
            likes_count=updated_post.get("likes_count", 0),
            comments_count=updated_post.get("comments_count", 0),
        )

    @staticmethod
    async def delete_post(post_id: str, current_user_id: str, is_admin: bool):
        db = await get_database()
        post = await db.posts.find_one({"_id": PostService.validate_object_id(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if str(post["author_id"]) != current_user_id and not is_admin:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        await db.posts.delete_one({"_id": PostService.validate_object_id(post_id)})
        await db.comments.delete_many({"post_id": PostService.validate_object_id(post_id)})
        await db.likes.delete_many({"post_id": PostService.validate_object_id(post_id)})
        return {"message": "Post deleted successfully"}

    @staticmethod
    async def create_comment(post_id: str, comment: CommentCreate, author_id: str, author_username: str) -> CommentResponse:
        db = await get_database()
        comment_dict = comment.dict()
        comment_dict["post_id"] = PostService.validate_object_id(post_id)
        comment_dict["author_id"] = PostService.validate_object_id(author_id)
        comment_dict["author_username"] = author_username
        comment_dict["created_at"] = datetime.utcnow()
        result = await db.comments.insert_one(comment_dict)
        created_comment = await db.comments.find_one({"_id": result.inserted_id})
        await db.posts.update_one({"_id": PostService.validate_object_id(post_id)}, {"$inc": {"comments_count": 1}})
        return CommentResponse(
            id=str(created_comment["_id"]),
            post_id=str(created_comment["post_id"]),
            author_id=str(created_comment["author_id"]),
            author_username=created_comment["author_username"],
            content=created_comment["content"],
            created_at=created_comment["created_at"],
        )

    @staticmethod
    async def get_comments(post_id: str, skip: int = 0, limit: int = 20):
        db = await get_database()
        comments = await db.comments.find({"post_id": PostService.validate_object_id(post_id)}).sort("created_at", 1).skip(skip).limit(limit).to_list(length=limit)
        return [CommentResponse(
            id=str(c["_id"]),
            post_id=str(c["post_id"]),
            author_id=str(c["author_id"]),
            author_username=c["author_username"],
            content=c["content"],
            created_at=c["created_at"]
        ) for c in comments]

    @staticmethod
    async def delete_comment(comment_id: str, current_user_id: str, is_admin: bool):
        db = await get_database()
        comment = await db.comments.find_one({"_id": PostService.validate_object_id(comment_id)})
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        if str(comment["author_id"]) != current_user_id and not is_admin:
            raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        await db.comments.delete_one({"_id": PostService.validate_object_id(comment_id)})
        await db.posts.update_one({"_id": comment["post_id"]}, {"$inc": {"comments_count": -1}})
        return {"message": "Comment deleted successfully"}

    @staticmethod
    async def like_post(post_id: str, user_id: str):
        db = await get_database()
        like = await db.likes.find_one({"post_id": PostService.validate_object_id(post_id), "user_id": PostService.validate_object_id(user_id)})
        if like:
            await db.likes.delete_one({"_id": like["_id"]})
            await db.posts.update_one({"_id": PostService.validate_object_id(post_id)}, {"$inc": {"likes_count": -1}})
            return {"message": "Like removed"}
        else:
            like_dict = {"post_id": PostService.validate_object_id(post_id), "user_id": PostService.validate_object_id(user_id), "created_at": datetime.utcnow()}
            await db.likes.insert_one(like_dict)
            await db.posts.update_one({"_id": PostService.validate_object_id(post_id)}, {"$inc": {"likes_count": 1}})
            return {"message": "Post liked"}

    @staticmethod
    async def get_feed(skip: int = 0, limit: int = 10):
        db = await get_database()
        posts = await db.posts.find({"is_published": True}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        return [PostResponse(
            id=str(post["_id"]),
            author_id=str(post["author_id"]),
            author_username=post["author_username"],
            title=post["title"],
            content=post["content"],
            tags=post.get("tags", []),
            image_url=post.get("image_url"),
            is_published=post.get("is_published", True),
            created_at=post["created_at"],
            updated_at=post["updated_at"],
            likes_count=post.get("likes_count", 0),
            comments_count=post.get("comments_count", 0),
        ) for post in posts]

    @staticmethod
    async def get_popular_posts(limit: int = 5):
        db = await get_database()
        posts = await db.posts.find({"is_published": True}).sort("likes_count", -1).limit(limit).to_list(length=limit)
        return [PostResponse(
            id=str(post["_id"]),
            author_id=str(post["author_id"]),
            author_username=post["author_username"],
            title=post["title"],
            content=post["content"],
            tags=post.get("tags", []),
            image_url=post.get("image_url"),
            is_published=post.get("is_published", True),
            created_at=post["created_at"],
            updated_at=post["updated_at"],
            likes_count=post.get("likes_count", 0),
            comments_count=post.get("comments_count", 0),
        ) for post in posts]

    @staticmethod
    def validate_object_id(oid: str):
        try:
            return ObjectId(oid)
        except bson_errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid ObjectId format") 