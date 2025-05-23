from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from ...models.blog import Article, ArticleCreate, ArticleResponse, Comment, CommentCreate, CommentResponse
from ...core.security import auth_handler
from ...db.database import get_db
from datetime import datetime
from bson import ObjectId
from python_slugify import slugify

router = APIRouter(prefix="/api/articles", tags=["Articles"])

@router.post("/", response_model=ArticleResponse)
async def create_article(
    article: ArticleCreate,
    db = Depends(get_db),
    current_user = Depends(auth_handler.get_current_user)
):
    """Создание новой статьи"""
    article_dict = article.dict()
    article_dict["author_id"] = ObjectId(current_user["_id"])
    article_dict["author_username"] = current_user["username"]
    article_dict["slug"] = slugify(article.title)
    article_dict["views"] = 0
    article_dict["likes"] = 0
    article_dict["created_at"] = datetime.utcnow()
    article_dict["updated_at"] = datetime.utcnow()
    article_dict["is_published"] = True
    
    result = await db.articles_collection.insert_one(article_dict)
    created_article = await db.articles_collection.find_one({"_id": result.inserted_id})
    
    return ArticleResponse(**created_article)

@router.get("/", response_model=List[ArticleResponse])
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = Query("created_at", enum=["created_at", "views", "likes"]),
    sort_order: Optional[str] = Query("desc", enum=["asc", "desc"]),
    db = Depends(get_db)
):
    """
    Получение списка статей с фильтрацией и поиском
    - category: фильтр по категории
    - tag: фильтр по тегу
    - search: поиск по заголовку и содержимому
    - author: фильтр по автору
    - sort_by: сортировка по полю (created_at, views, likes)
    - sort_order: порядок сортировки (asc, desc)
    """
    filter_query = {"is_published": True}
    
    if category:
        filter_query["category"] = category
    if tag:
        filter_query["tags"] = tag
    if author:
        filter_query["author_username"] = author
    if search:
        filter_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}}
        ]
    
    # Настройка сортировки
    sort_direction = -1 if sort_order == "desc" else 1
    
    cursor = db.articles_collection.find(filter_query)
    cursor.sort(sort_by, sort_direction).skip(skip).limit(limit)
    
    articles = await cursor.to_list(length=limit)
    return [ArticleResponse(**article) for article in articles]

@router.get("/categories")
async def get_categories(db = Depends(get_db)):
    """Получение списка всех категорий"""
    categories = await db.articles_collection.distinct("category")
    return {"categories": categories}

@router.get("/tags")
async def get_tags(db = Depends(get_db)):
    """Получение списка всех тегов"""
    tags = await db.articles_collection.distinct("tags")
    return {"tags": tags}

@router.get("/popular", response_model=List[ArticleResponse])
async def get_popular_articles(
    limit: int = Query(5, ge=1, le=20),
    db = Depends(get_db)
):
    """Получение популярных статей (по количеству просмотров)"""
    articles = await db.articles_collection.find(
        {"is_published": True}
    ).sort("views", -1).limit(limit).to_list(length=limit)
    
    return [ArticleResponse(**article) for article in articles]

@router.get("/{slug}", response_model=ArticleResponse)
async def get_article(
    slug: str,
    db = Depends(get_db)
):
    """Получение статьи по slug"""
    article = await db.articles_collection.find_one_and_update(
        {"slug": slug},
        {"$inc": {"views": 1}},
        return_document=True
    )
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return ArticleResponse(**article)

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: str,
    article_update: ArticleCreate,
    db = Depends(get_db),
    current_user = Depends(auth_handler.get_current_user)
):
    """Обновление статьи"""
    article = await db.articles_collection.find_one({"_id": ObjectId(article_id)})
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if str(article["author_id"]) != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this article")
    
    update_data = article_update.dict()
    update_data["updated_at"] = datetime.utcnow()
    update_data["slug"] = slugify(article_update.title)
    
    updated_article = await db.articles_collection.find_one_and_update(
        {"_id": ObjectId(article_id)},
        {"$set": update_data},
        return_document=True
    )
    
    return ArticleResponse(**updated_article)

@router.patch("/{article_id}/publish")
async def toggle_article_publication(
    article_id: str,
    is_published: bool = Body(...),
    db = Depends(get_db),
    current_user = Depends(auth_handler.get_current_user)
):
    """Публикация/снятие с публикации статьи"""
    article = await db.articles_collection.find_one({"_id": ObjectId(article_id)})
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if str(article["author_id"]) != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this article")
    
    await db.articles_collection.update_one(
        {"_id": ObjectId(article_id)},
        {"$set": {"is_published": is_published}}
    )
    
    return {"message": "Article publication status updated"}

@router.delete("/{article_id}")
async def delete_article(
    article_id: str,
    db = Depends(get_db),
    current_user = Depends(auth_handler.get_current_user)
):
    """Удаление статьи"""
    article = await db.articles_collection.find_one({"_id": ObjectId(article_id)})
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if str(article["author_id"]) != str(current_user["_id"]) and not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this article")
    
    await db.articles_collection.delete_one({"_id": ObjectId(article_id)})
    await db.comments_collection.delete_many({"article_id": ObjectId(article_id)})
    await db.likes_collection.delete_many({"article_id": article_id})
    
    return {"message": "Article deleted successfully"}

@router.post("/{article_id}/like")
async def like_article(
    article_id: str,
    db = Depends(get_db),
    current_user = Depends(auth_handler.get_current_user)
):
    """Поставить/убрать лайк статье"""
    article = await db.articles_collection.find_one({"_id": ObjectId(article_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    user_id = str(current_user["_id"])
    likes_collection = db.likes_collection
    
    existing_like = await likes_collection.find_one({
        "user_id": user_id,
        "article_id": article_id
    })
    
    if existing_like:
        await likes_collection.delete_one({"_id": existing_like["_id"]})
        await db.articles_collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$inc": {"likes": -1}}
        )
        return {"message": "Like removed"}
    else:
        await likes_collection.insert_one({
            "user_id": user_id,
            "article_id": article_id,
            "created_at": datetime.utcnow()
        })
        await db.articles_collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$inc": {"likes": 1}}
        )
        return {"message": "Article liked"}

# Маршруты для комментариев
@router.post("/{article_id}/comments", response_model=CommentResponse)
async def create_comment(
    article_id: str,
    comment: CommentCreate,
    db = Depends(get_db),
    current_user = Depends(auth_handler.get_current_user)
):
    """Создание комментария к статье"""
    article = await db.articles_collection.find_one({"_id": ObjectId(article_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    comment_dict = comment.dict()
    comment_dict["article_id"] = ObjectId(article_id)
    comment_dict["author_id"] = ObjectId(current_user["_id"])
    comment_dict["author_username"] = current_user["username"]
    comment_dict["created_at"] = datetime.utcnow()
    
    result = await db.comments_collection.insert_one(comment_dict)
    created_comment = await db.comments_collection.find_one({"_id": result.inserted_id})
    
    return CommentResponse(**created_comment)

@router.get("/{article_id}/comments", response_model=List[CommentResponse])
async def get_article_comments(
    article_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db = Depends(get_db)
):
    """Получение комментариев к статье"""
    comments = await db.comments_collection.find(
        {"article_id": ObjectId(article_id)}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return [CommentResponse(**comment) for comment in comments] 