# backend/src/api/routes/foods.py
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from backend.src.core.security import auth_handler
from backend.src.core.config import logger
from backend.src.db.database import get_db
from backend.src.models.tables import Foods, Users
from backend.src.schemas.pydantic_models import FoodResponse, FoodCreate

# Создаем маршрутизатор
food_router = APIRouter(prefix="/food", tags=["Food"])


@food_router.post("/food/", response_model=FoodResponse)
async def add_food(
    data: FoodCreate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(auth_handler.get_current_user),
):
    """
    Add a new food item to the database.

    Parameters:
    - data: FoodCreate - The food data to be added (name, calories, carbs, fats, proteins).

    Returns:
    - FoodResponse: The created food item.
    """
    try:
        # Проверка на существование продукта
        existing_food = await Foods.get_by_username(db, data.name, current_user.id)
        if existing_food:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Продукт с таким названием уже существует",
            )

        # Создаем новый объект Food
        new_food = Foods(
            name=data.name,
            calories=data.calories,
            carbs=data.carbs,
            fats=data.fats,
            proteins=data.proteins,
            user_id=current_user.id,
        )

        # Сохранение в базу данных
        db.add(new_food)
        await db.commit()
        await db.refresh(new_food)

        return FoodResponse.model_validate(new_food)

    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Ошибка базы данных при добавлении продукта для пользователя {current_user.id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Ошибка при добавлении продукта для пользователя {current_user.id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )
