from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ...core.auth import AuthHandler
from ...models.blog import User, UserCreate, Token
from ...db.database import get_db
from datetime import datetime

auth_router = APIRouter()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@auth_router.post("/register", response_model=Token)
async def register(user: UserCreate, db = Depends(get_db)):
    # Проверяем, существует ли пользователь
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Создаем нового пользователя
    hashed_password = auth_handler.get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    # Создаем токены
    access_token = auth_handler.create_access_token(user_dict)
    refresh_token = auth_handler.create_refresh_token(user_dict)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@auth_router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = await db.users.find_one({"username": form_data.username})
    if not user or not auth_handler.verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_handler.create_access_token(user)
    refresh_token = auth_handler.create_refresh_token(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db = Depends(get_db)):
    try:
        payload = auth_handler.decode_token(refresh_token)
        user = await db.users.find_one({"_id": payload["sub"]})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        access_token = auth_handler.create_access_token(user)
        new_refresh_token = auth_handler.create_refresh_token(user)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        ) 