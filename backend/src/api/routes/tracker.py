from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from typing import List

from ...core.config import logger
from ...core.security import auth_handler
from ...db.database import get_db
from ...models.tables import Tracker, Foods, Users
from ...schemas.pydantic_models import TrackerResponse, TrackerCreate, TrackerUpdate
from ...schemas.pydantic_models import FoodResponse

tracker_router = APIRouter(tags=["Tracker"])


@tracker_router.post("/tracker/add-food", response_model=TrackerResponse)
async def add_food_to_tracker(
    food_id: int,
    current_user: Users = Depends(auth_handler.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Добавляет еду в трекер пользователя за текущий день.
    Если запись трекера за сегодня ещё не существует, создаёт новую.
    """
    try:
        # Проверяем, существует ли еда
        food_query = select(Foods).where(
            Foods.id == food_id, Foods.user_id == current_user.id
        )
        food_result = await db.execute(food_query)
        food = food_result.scalar_one_or_none()
        if not food:
            logger.warning(
                f"Food with ID {food_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found or does not belong to user",
            )

        # Получаем текущую дату
        today = date.today()

        # Проверяем, есть ли запись трекера за сегодня
        tracker = await Tracker.get_by_user_and_date(db, current_user.id, today)
        if not tracker:
            # Создаём новую запись трекера
            tracker_data = TrackerCreate(
                user_id=current_user.id,
                date=today,
                calories=0.0,
                carbs=0.0,
                fats=0.0,
                proteins=0.0,
            )
            tracker = Tracker(**tracker_data.model_dump())
            db.add(tracker)
            await db.commit()
            await db.refresh(tracker)
            logger.info(f"Created new tracker for user {current_user.id} on {today}")

        # Обновляем значения трекера
        tracker.calories += food.calories
        tracker.carbs += food.carbs
        tracker.fats += food.fats
        tracker.proteins += food.proteins

        await db.commit()
        await db.refresh(tracker)
        logger.info(f"Updated tracker for user {current_user.id} with food {food.name}")

        return TrackerResponse.model_validate(tracker)

    except SQLAlchemyError as e:
        logger.error(f"Database error while adding food to tracker: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while adding food to tracker: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@tracker_router.get("/tracker/today", response_model=TrackerResponse)
async def get_today_tracker(
    current_user: Users = Depends(auth_handler.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получает данные трекера за текущий день.
    """
    try:
        today = date.today()
        tracker = await Tracker.get_by_user_and_date(db, current_user.id, today)
        if not tracker:
            logger.info(f"No tracker found for user {current_user.id} on {today}")
            # Возвращаем пустой трекер
            tracker_data = TrackerCreate(
                user_id=current_user.id,
                date=today,
                calories=0.0,
                carbs=0.0,
                fats=0.0,
                proteins=0.0,
            )
            tracker = Tracker(**tracker_data.model_dump())
            db.add(tracker)
            await db.commit()
            await db.refresh(tracker)
            logger.info(f"Created empty tracker for user {current_user.id} on {today}")

        return TrackerResponse.model_validate(tracker)

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching tracker: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching tracker: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@tracker_router.get("/tracker/foods/today", response_model=List[FoodResponse])
async def get_today_foods(
    current_user: Users = Depends(auth_handler.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получает список еды, добавленной пользователем за текущий день.
    """
    try:
        today = date.today()
        food_query = select(Foods).where(
            Foods.user_id == current_user.id, func.date(Foods.created_at) == today
        )
        food_result = await db.execute(food_query)
        foods = food_result.scalars().all()

        logger.info(f"Found {len(foods)} foods for user {current_user.id} on {today}")
        return [FoodResponse.model_validate(food) for food in foods]

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching foods: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching foods: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
