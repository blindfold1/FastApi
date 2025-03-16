import os
from fastapi import HTTPException, APIRouter
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext

from src.config import DATABASE_URL,SECRET_KEY,ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM


auth_router = APIRouter(prefix="/token", tags=["Token"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@auth_router.post("/user_login")
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire.timestamp()
    to_encode["sub"] = data.get("sub", "unknown")
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "token_type": "bearer"}

@auth_router.post("/verify")
def verify_user(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

@auth_router.post("/password")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@auth_router.post("/decode")
def decode_access_token(access_token: str):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
