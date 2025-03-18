from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import AuthHandler
from src.db.dependencies import get_db
from src.models.user import Users
from src.schemas.pydantic_models import Token

auth_router = APIRouter(tags=["Authentication"])
auth_handler = AuthHandler()

@auth_router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await Users.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials"
        )

    access_token = auth_handler.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=15)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me")
async def read_me(
    current_user: Users = Depends(auth_handler.get_current_user)
):
    return current_user