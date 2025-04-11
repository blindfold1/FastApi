from datetime import timedelta

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.token import refresh_token_scheme, credentials_exception
from ...core.config import logger, settings
from ...core.security import auth_handler
from ...db.database import get_db
from ...models.tables import Users
from ...schemas import UserResponse
from ...schemas.token import Token

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
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
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
            )

        # Проверка, активен ли пользователь
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User is not active"
            )

        # Создание токенов
        access_token = auth_handler.create_access_token(
            data={"sub": user.username}, expires_delta=timedelta(minutes=15)
        )

        refresh_token = auth_handler.create_refresh_token(
            data={"sub": user.username}, expires_delta=timedelta(days=30)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }

    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        logger.error(
            f"Database error during login for username {form_data.username}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    except Exception as e:
        logger.error(f"Error during login for username {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@auth_router.get("/me", response_model=UserResponse)
async def read_me(
    current_user: Users = Depends(auth_handler.get_current_user),
    db: AsyncSession = Depends(get_db),
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
            detail="Internal server error",
        )
    except Exception as e:
        logger.error(f"Error while fetching user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    token: str = Depends(refresh_token_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = auth_handler.decode_token(token)
        if not payload:
            raise credentials_exception
        username = payload.get("sub")
        if not username:
            raise credentials_exception

        user = await Users.get_by_username(db, username)
        if not user:
            raise credentials_exception

        new_access_token = auth_handler.create_access_token(
            data={"sub": user.username, "scopes": user.scope},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        new_refresh_token = auth_handler.create_refresh_token(
            data={"sub": user.username}, expires_delta=timedelta(days=30)
        )
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
