import jwt
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends, APIRouter, Body, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import AuthHandler, oauth2_scheme, auth_handler
from src.core.config import settings, logger
from src.db.database import get_db
from src.db.dependencies import SessionDep
from src.models.user import Users
from src.schemas.pydantic_models import UserCreate, UserUpdate, UserResponse

clients_router = APIRouter(prefix="/clients", tags=["Clients"])




@clients_router.post("/users", response_model=UserResponse)
async def create_user(
        data: UserCreate = Body(...),
        db: AsyncSession = Depends(get_db)
):
    try:
        # Проверка на существование пользователя
        existing_user = await Users.get_by_username(db, data.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Имя пользователя уже существует")

        # Проверка, что пароль передан
        if not data.password:
            logger.error("Password not provided in request")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required")

        # Хеширование пароля
        hashed_password = auth_handler.get_password_hash(data.password)
        new_user = Users(**data.model_dump(exclude={"password"}), password_hash=hashed_password)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserResponse(
            id=new_user.id,
            name=new_user.name,
            weight=new_user.weight,
            height=new_user.height,
            age=new_user.age,
            username=new_user.username,
            is_active=new_user.is_active
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {e}")
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")
@clients_router.get("/users", response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Users))
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]
    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@clients_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int = Path(..., description="ID пользователя"),
        updated_data: UserUpdate = Body(..., description="Новые данные"),
        db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Users).filter(Users.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        for key, value in updated_data.dict(exclude_unset=True).items():
            setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        return UserResponse.model_validate(user)
    except SQLAlchemyError as error:
        await db.rollback()
        logger.error(f"Database error: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@clients_router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
        user_id: int = Path(..., description="ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Users).filter(Users.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await db.delete(user)
        await db.commit()
        return UserResponse.model_validate(user)
    except SQLAlchemyError as error:
        await db.rollback()
        logger.error(f"Database error: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@clients_router.get("/")
def test_schema():
    return UserCreate.model_json_schema()