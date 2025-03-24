from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from passlib.context import CryptContext
import jwt
from typing import Optional
from backend.src.core.config import settings
from backend.src.db.database import get_db
from backend.src.models.user import Users

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class AuthHandler:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=30))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)


    @staticmethod
    def verify_password( plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)


    @staticmethod
    def get_password_hash( password: str):
        return pwd_context.hash(password)

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception


        user = await Users.get_by_username(db, username=username)
        if user is None:
            raise credentials_exception
        return user

auth_handler = AuthHandler()