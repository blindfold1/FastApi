from fastapi import APIRouter, Depends, HTTPException, status, Query
from ...models.post import PostCreate, PostResponse, CommentCreate, CommentResponse
from ...services.post_service import PostService
from ...core.security import auth_handler

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse)
async def create_post(post: PostCreate, current_user=Depends(auth_handler.get_current_user)):
    return await PostService.create_post(post, author_id=current_user["_id"], author_username=current_user["username"])

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    return await PostService.get_post(post_id)

@router.get("/", response_model=list[PostResponse])
async def get_posts(skip: int = 0, limit: int = 10, search: str = Query(None), tag: str = Query(None)):
    return await PostService.get_posts(skip=skip, limit=limit, search=search, tag=tag)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, post_update: PostCreate, current_user=Depends(auth_handler.get_current_user)):
    is_admin = current_user.get("role") == "admin"
    return await PostService.update_post(post_id, post_update, current_user_id=current_user["_id"], is_admin=is_admin)

@router.delete("/{post_id}")
async def delete_post(post_id: str, current_user=Depends(auth_handler.get_current_user)):
    is_admin = current_user.get("role") == "admin"
    return await PostService.delete_post(post_id, current_user_id=current_user["_id"], is_admin=is_admin)

@router.post("/{post_id}/comments", response_model=CommentResponse)
async def create_comment(post_id: str, comment: CommentCreate, current_user=Depends(auth_handler.get_current_user)):
    return await PostService.create_comment(post_id, comment, author_id=current_user["_id"], author_username=current_user["username"])

@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(post_id: str, skip: int = 0, limit: int = 20):
    return await PostService.get_comments(post_id, skip=skip, limit=limit)

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, current_user=Depends(auth_handler.get_current_user)):
    is_admin = current_user.get("role") == "admin"
    return await PostService.delete_comment(comment_id, current_user_id=current_user["_id"], is_admin=is_admin)

@router.post("/{post_id}/like")
async def like_post(post_id: str, current_user=Depends(auth_handler.get_current_user)):
    return await PostService.like_post(post_id, user_id=current_user["_id"])

@router.get("/feed", response_model=list[PostResponse])
async def get_feed(skip: int = 0, limit: int = 10):
    return await PostService.get_feed(skip=skip, limit=limit)

@router.get("/popular", response_model=list[PostResponse])
async def get_popular_posts(limit: int = 5):
    return await PostService.get_popular_posts(limit=limit) 