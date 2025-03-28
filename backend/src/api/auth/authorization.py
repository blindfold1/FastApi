from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from backend.src.core.security import auth_handler
from backend.src.core.config import logger
from backend.src.db.database import get_db
from backend.src.models.tables import Users
from backend.src.schemas import UserResponse
from backend.src.schemas.token import Token

# Создаем маршрутизатор
login_router = APIRouter(tags=["Authentication"])

@login_router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate a user and return access and refresh tokens.

    Parameters:
    - form_data: OAuth2PasswordRequestForm - Username and password for authentication.

    Returns:
    - Token: Access and refresh tokens.
    """
    try:
        # Аутентификация пользователя
        user = await Users.authenticate(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials"
            )

        # Проверка, активен ли пользователь
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not active"
            )

        # Создание токенов
        access_token = auth_handler.create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=15)
        )

        refresh_token = auth_handler.create_refresh_token(
            data={"sub": user.username},
            expires_delta=timedelta(days=30)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token
        }

    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        logger.error(f"Database error during login for username {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    except Exception as e:
        logger.error(f"Error during login for username {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@login_router.get("/me", response_model=UserResponse)
async def read_me(
    current_user: Users = Depends(auth_handler.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current authenticated user's information.

    Returns:
    - UserResponse: The current user's data.
    """
    try:
        # Обновляем данные пользователя из базы данных
        await db.refresh(current_user)
        return UserResponse.model_validate(current_user)

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    except Exception as e:
        logger.error(f"Error while fetching user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )