from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from ...models.blog import Post, Comment, User
from ...db.database import db, get_db
from ...core.auth import get_current_user
from ...core.config import settings
from datetime import datetime
from bson import ObjectId
import re

def slugify(text: str) -> str:
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    # Remove all non-word characters (except hyphens)
    text = re.sub(r'[^\w\-]', '', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Remove leading and trailing hyphens
    text = text.strip('-')
    return text

router = APIRouter(prefix="/api/v1/blog", tags=["blog"])

# Posts routes
@router.post("/posts/", response_model=Post)
async def create_post(
    post: Post,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    post.author_id = current_user.id
    post.slug = slugify(post.title)
    result = await db.posts_collection.insert_one(post.dict(by_alias=True))
    created_post = await db.posts_collection.find_one({"_id": result.inserted_id})
    return Post(**created_post)

@router.get("/posts/", response_model=List[Post])
async def get_posts(
    skip: int = 0,
    limit: int = 10,
    db = Depends(get_db)
):
    posts = await db.posts_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return [Post(**post) for post in posts]

@router.get("/posts/{slug}", response_model=Post)
async def get_post(
    slug: str,
    db = Depends(get_db)
):
    if (post := await db.posts_collection.find_one({"slug": slug})) is not None:
        return Post(**post)
    raise HTTPException(status_code=404, detail="Post not found")

@router.put("/posts/{post_id}", response_model=Post)
async def update_post(
    post_id: str,
    post_update: Post,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    post = await db.posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["author_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    post_update.updated_at = datetime.utcnow()
    update_result = await db.posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": post_update.dict(exclude={"id", "author_id"}, by_alias=True)}
    )
    
    if update_result.modified_count == 1:
        updated_post = await db.posts_collection.find_one({"_id": ObjectId(post_id)})
        return Post(**updated_post)
    raise HTTPException(status_code=404, detail="Post not found")

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    post = await db.posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["author_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    delete_result = await db.posts_collection.delete_one({"_id": ObjectId(post_id)})
    if delete_result.deleted_count == 1:
        return {"message": "Post deleted successfully"}
    raise HTTPException(status_code=404, detail="Post not found")

# Comments routes
@router.post("/posts/{post_id}/comments/", response_model=Comment)
async def create_comment(
    post_id: str,
    comment: Comment,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    comment.post_id = ObjectId(post_id)
    comment.author_id = current_user.id
    result = await db.comments_collection.insert_one(comment.dict(by_alias=True))
    created_comment = await db.comments_collection.find_one({"_id": result.inserted_id})
    return Comment(**created_comment)

@router.get("/posts/{post_id}/comments/", response_model=List[Comment])
async def get_comments(
    post_id: str,
    skip: int = 0,
    limit: int = 10,
    db = Depends(get_db)
):
    comments = await db.comments_collection.find(
        {"post_id": ObjectId(post_id)}
    ).skip(skip).limit(limit).to_list(length=limit)
    return [Comment(**comment) for comment in comments]

# File upload route
@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create upload directory if it doesn't exist
    upload_dir = settings.UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_exist=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{current_user.id}.{file_extension}"
    file_path = upload_dir / filename
    
    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {
        "filename": filename,
        "url": f"/static/uploads/{filename}"
    } 