import jwt
from sqlalchemy import select, delete, or_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user

from src.api.auth.token import SECRET_KEY, ALGORITHM, oauth2_scheme
from src.api.dependencies import SessionDep, pwd_context
from src.config import logger
from src.models.model import Users
from src.pydantic_models import User_Schema, Updated_User_Schema

clients_router = APIRouter(prefix="/clients", tags=["Clients"])



@clients_router.post("/users")
async def create_user(data: User_Schema, db: AsyncSession = Depends(SessionDep)):
    try:
        hashed_password = pwd_context.hash(data.password)
        new_user = Users(
            name=data.name,
            weight=data.weight,
            height=data.height,
            age=data.age,
            username=data.username,
            password_hash=hashed_password
        )
        db.add(new_user)
        await db.commit()
        return {"Success": True}
    except SQLAlchemyError as error:
        logger.error(f"Database error: {error}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as error:
        logger.error(f"Unexpected error: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")


@clients_router.get("/users")
async def get_users(db: AsyncSession = Depends(SessionDep)):
    try:
        result = await db.execute(select(Users))  # ✅ Используем `db`
        users = result.scalars().all()
        return users
    except SQLAlchemyError as error:
        logger.error(f"No users found: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@clients_router.get("/me", response_model=User_Schema)
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(SessionDep)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})


    result = await db.execute(select(Users).filter(Users.username == username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@clients_router.put("/update", response_model=User_Schema)
async def update_user(user_id:int,updated_data: Updated_User_Schema, db: AsyncSession = Depends(SessionDep)):
    try:
        result = await db.execute(select(Users).filter(Users.id == user_id))

        updated_user = result.scalars().first()

        updated_data = updated_data.dict(exclude_unset=True)
        for age, weight in updated_data.items():
            setattr(updated_user, age, weight)

        await db.commit()
        await db.refresh(updated_user)

    except SQLAlchemyError as error:
        logger.error(f"Database error: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return updated_user

@clients_router.delete("/delete", response_model = User_Schema)
async def delete_user(user_id:int,user_name:str, db: AsyncSession = Depends(SessionDep)):
    try:
        result = await db.execute(select(Users).filter(Users.id == user_id))
        user_for_delete = result.scalars().first()
        if not user_for_delete:
            raise HTTPException(status_code=404, detail="User not found")

        await db.execute(delete(Users).where(or_(Users.id == user_id, Users.name == user_name)))
        await db.commit()
    except SQLAlchemyError as error:
        logger.error(f"Database error: {error}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return user
