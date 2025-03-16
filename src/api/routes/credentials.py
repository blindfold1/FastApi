

from sqlalchemy import select
from fastapi import  HTTPException, APIRouter

from src.api.dependencies import SessionDep, pwd_context

from src.config import logger
from src.models.model import Users
from src.pydantic_models import User_Credentials

credentials_router = APIRouter(prefix="/credentials", tags=["Credentials"])
@credentials_router.post("/users/create_credentials")
async def create_user_credentials(data: User_Credentials, session: SessionDep):
    try:
        username_check = await session.execute(select(Users).where(Users.username == data.username))
        user = username_check.scalars().first()

        if user:
            raise HTTPException(status_code=400, detail="User with this username already exists")

        hashed_password = pwd_context.hash(data.password)
        new_user = Users(username=data.username, password_hash=hashed_password)
        session.add(new_user)
        await session.flush()
        await session.commit()
        return {"message":"Success"}
    except Exception as incorrect_credentials_error:
        logger.error(f"Incorrect credentials: {incorrect_credentials_error}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

