# backend/src/api/routes/clients.py
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    APIRouter,
    Body,
    Path,
    status,
    Request,
)
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, NoSuchTableError
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import logger
from ...core.security import auth_handler
from ...db.database import get_db, engine
from ...models.tables import Users
from ...schemas.pydantic_models import UserCreate, UserUpdate, UserResponse

app = FastAPI()

clients_router = APIRouter(tags=["Clients"])
app.include_router(clients_router)


# Проверка подключения к базе данных при запуске
async def check_db_connection():
    try:
        async with engine.connect() as connection:
            await connection.scalar(select(1))
        logger.info("Successfully connected to the database")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {str(e)}", exc_info=True)
        raise


# Проверка существования таблицы
async def check_table_exists(db: AsyncSession):
    try:
        # Проверяем существование таблицы через SQL-запрос
        await db.execute(select(1).select_from(Users).limit(1))
        logger.info("Table 'users' exists and is accessible")
    except SQLAlchemyError as e:
        logger.error(
            f"Table 'users' does not exist or is not accessible: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Table 'users' does not exist or is not accessible. Please run migrations.",
        )


# Middleware для логирования всех запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


# Остальной код (маршруты) остаётся без изменений
@clients_router.post("/users", response_model=UserResponse)
async def create_user(data: UserCreate = Body(...), db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating user with username: {data.username}")
    try:
        # Проверка существования таблицы
        await check_table_exists(db)

        # Проверка на существование пользователя
        existing_user = await Users.get_by_username(db, data.username)
        if existing_user:
            logger.warning(f"User with username {data.username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя пользователя уже существует",
            )

        # Проверка, что пароль передан
        if not data.password:
            logger.error("Password not provided in request")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required"
            )

        # Хеширование пароля
        hashed_password = auth_handler.get_password_hash(data.password)
        new_user = Users(
            **data.model_dump(exclude={"password"}), password_hash=hashed_password
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"User {data.username} created successfully with ID {new_user.id}")
        return UserResponse.model_validate(new_user)

    except HTTPException as e:
        raise e
    except NoSuchTableError as e:
        logger.error(f"Table 'users' does not exist: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Table 'users' does not exist. Please run migrations.",
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@clients_router.get("/users", response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    logger.info("Fetching all users")
    try:
        # Проверка существования таблицы
        await check_table_exists(db)

        result = await db.execute(select(Users))
        users = result.scalars().all()
        if not users:
            logger.warning("No users found in the database")
            return []
        logger.info(f"Found {len(users)} users")
        return [UserResponse.model_validate(user) for user in users]
    except NoSuchTableError as e:
        logger.error(f"Table 'users' does not exist: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Table 'users' does not exist. Please run migrations.",
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


@clients_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int = Path(..., description="ID пользователя"),
    updated_data: UserUpdate = Body(..., description="Новые данные"),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Updating user with ID {user_id}")
    try:
        # Проверка существования таблицы
        await check_table_exists(db)

        result = await db.execute(select(Users).filter(Users.id == user_id))
        user = result.scalars().first()
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        for key, value in updated_data.dict(exclude_unset=True).items():
            setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        logger.info(f"User with ID {user_id} updated successfully")
        return UserResponse.model_validate(user)
    except NoSuchTableError as e:
        logger.error(f"Table 'users' does not exist: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Table 'users' does not exist. Please run migrations.",
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating user: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


@clients_router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int = Path(..., description="ID пользователя"),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Deleting user with ID {user_id}")
    try:
        # Проверка существования таблицы
        await check_table_exists(db)

        result = await db.execute(select(Users).filter(Users.id == user_id))
        user = result.scalars().first()
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await db.delete(user)
        await db.commit()
        logger.info(f"User with ID {user_id} deleted successfully")
        return UserResponse.model_validate(user)
    except NoSuchTableError as e:
        logger.error(f"Table 'users' does not exist: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Table 'users' does not exist. Please run migrations.",
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting user: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
