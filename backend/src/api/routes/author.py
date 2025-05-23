from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from ..auth.token import refresh_token_scheme, credentials_exception
from ...core.config import logger, settings
from ...core.security import auth_handler
from ...db.database import get_db
from ...models.blog import User
from bson import ObjectId

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@auth_router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db)
):
    try:
        # Находим пользователя по имени
        user_doc = await db.users_collection.find_one({"username": form_data.username})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Проверяем пароль
        if not pwd_context.verify(form_data.password, user_doc["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Проверяем активность пользователя
        if not user_doc.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not active"
            )

        # Создаем токены
        access_token = auth_handler.create_access_token(
            data={"sub": form_data.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = auth_handler.create_refresh_token(
            data={"sub": form_data.username},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@auth_router.post("/register")
async def register(
    username: str,
    email: str,
    password: str,
    db = Depends(get_db)
):
    try:
        # Проверяем, существует ли пользователь
        existing_user = await db.users_collection.find_one({"username": username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Хешируем пароль
        hashed_password = pwd_context.hash(password)

        # Создаем нового пользователя
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )

        # Сохраняем в базу
        result = await db.users_collection.insert_one(user.dict(by_alias=True))
        
        return {"message": "User registered successfully", "user_id": str(result.inserted_id)}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@auth_router.post("/refresh")
async def refresh_token(
    token: str = Depends(refresh_token_scheme),
    db = Depends(get_db)
):
    try:
        # Проверяем refresh token
        payload = auth_handler.decode_token(token)
        if not payload:
            raise credentials_exception
        
        username = payload.get("sub")
        if not username:
            raise credentials_exception

        # Проверяем существование пользователя
        user = await db.users_collection.find_one({"username": username})
        if not user:
            raise credentials_exception

        # Создаем новые токены
        new_access_token = auth_handler.create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        new_refresh_token = auth_handler.create_refresh_token(
            data={"sub": username},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
