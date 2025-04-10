# backend/src/api/routes/foods.py
import os
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from ...core.config import logger
from ...core.security import auth_handler
from ...db.database import get_db
from ...models.tables import Foods
from ...schemas.pydantic_models import FoodResponse

food_router = APIRouter(tags=["Foods"])

USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
logger.info(f"Using USDA API Key: {USDA_API_KEY}")
USDA_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


@food_router.post("/food/search-and-add-food/", response_model=FoodResponse)
async def search_and_add_food(
    name: str = Body(...),
    exact_match: bool = Body(False),
    data_type: str = Body("Foundation"),
    current_user=Depends(auth_handler.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Searching for food '{name}' in USDA API for user {current_user.id}")

    data_types_to_try = [data_type, "Survey (FNDDS)", "Branded", "SR Legacy"]
    food_data = None

    for dt in data_types_to_try:
        params = {
            "query": name,
            "dataType": [dt],
            "requireAllWords": str(exact_match).lower(),
            "pageSize": 1,
            "api_key": USDA_API_KEY,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(USDA_API_URL, params=params)
                response.raise_for_status()
                data = response.json()

            if data.get("foods"):
                food_data = data["foods"][0]
                logger.info(f"Food found with data_type '{dt}'")
                break

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.error(
                    f"USDA API returned 403 Forbidden: Check your API key or rate limits"
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="USDA API access denied: Invalid API key or rate limit exceeded. Please try again later or contact support.",
                )
            logger.error(
                f"USDA API error with data_type '{dt}': {str(e)}", exc_info=True
            )
            if dt == data_types_to_try[-1]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Error querying USDA API: {str(e)}",
                )
            continue

    if not food_data:
        logger.warning(f"No food found for query '{name}' after trying all data types")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No food found for query '{name}'",
        )

    nutrients = {}
    for nutrient in food_data.get("foodNutrients", []):
        if "nutrientName" not in nutrient or "value" not in nutrient:
            logger.warning(f"Skipping malformed nutrient: {nutrient}")
            continue
        nutrient_name = nutrient["nutrientName"].lower()
        value = float(nutrient["value"])
        unit = nutrient.get("unitName", "").upper()

        if nutrient_name == "energy" and unit == "KJ":
            value = value / 4.184  # 1 kJ = 0.239 kcal
        nutrients[nutrient_name] = value

    calories = nutrients.get("energy", 0.0)
    proteins = nutrients.get("protein", 0.0)
    fats = nutrients.get("total lipid (fat)", 0.0)
    carbs = nutrients.get("carbohydrate, by difference", 0.0)
    vitamin_c = nutrients.get("vitamin c, total ascorbic acid", 0.0)
    calcium = nutrients.get("calcium, ca", 0.0)

    new_food = Foods(
        name=food_data.get("description", name),
        calories=calories,
        proteins=proteins,
        fats=fats,
        carbs=carbs,
        vitamin_c=vitamin_c,
        calcium=calcium,
        user_id=current_user.id,
    )
    db.add(new_food)
    await db.commit()
    await db.refresh(new_food)
    logger.info(f"Food '{new_food.name}' added successfully for user {current_user.id}")
    return FoodResponse.model_validate(new_food)


@food_router.post("/food/food/", response_model=FoodResponse)
async def add_food(
    name: str = Body(...),
    calories: float = Body(...),
    proteins: float = Body(...),  # Change to float
    fats: float = Body(...),
    carbs: float = Body(...),  # Change to float
    vitamin_c: float = Body(0.0),
    calcium: float = Body(0.0),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Adding food {name} without user association")
    try:
        new_food = Foods(
            name=name,
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbs=carbs,
            vitamin_c=vitamin_c,
            calcium=calcium,
        )
        db.add(new_food)
        await db.commit()
        await db.refresh(new_food)
        logger.info(f"Food {name} added successfully")
        return FoodResponse.model_validate(new_food)
    except SQLAlchemyError as e:
        logger.error(f"Database error while adding food: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
