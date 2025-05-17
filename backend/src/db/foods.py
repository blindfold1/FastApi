from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import auth_handler
from src.core.config import settings, logger
from src.db.database import get_db
from src.db.mongo import MongoDB
from src.utils.food_parses import parse_food_nutrients
from src.custom_serializer.formats.json_serializer import JsonSerializer
import httpx
from datetime import datetime

router = APIRouter(tags=["Foods"])
mongo = MongoDB()
serializer = JsonSerializer()

@router.post("/food/search-and-add", response_model=dict)
async def search_and_add_food(
    name: str = Body(...),
    exact_match: bool = Body(False),
    current_user=Depends(auth_handler.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Searching for food '{name}' for user {current_user.id}")
    # Проверка кэша в MongoDB
    cached_food = await mongo.get_food(name, current_user.id)
    if cached_food:
        logger.info(f"Food '{name}' found in cache")
        return cached_food

    # Запрос к USDA API
    async with httpx.AsyncClient(timeout=10.0) as client:
        params = {
            "query": name,
            "requireAllWords": str(exact_match).lower(),
            "pageSize": 1,
            "api_key": settings.USDA_API_KEY
        }
        response = await client.get("https://api.nal.usda.gov/fdc/v1/foods/search", params=params)
        response.raise_for_status()
        data = response.json()

    if not data.get("foods"):
        raise HTTPException(status_code=404, detail="Food not found")

    food_data = parse_food_nutrients(data["foods"][0])
    food_data.update({
        "name": name,
        "user_id": current_user.id,
        "created_at": datetime.utcnow().isoformat()
    })

    # Сохранение в MongoDB
    food_id = await mongo.save_food(food_data)
    logger.info(f"Food '{name}' saved with ID {food_id}")

    # Сохранение в файл для логов через custom_serializer
    serializer.save_to_file(food_data, f"logs/food_{name}_{current_user.id}.txt")

    return {"id": food_id, **food_data}