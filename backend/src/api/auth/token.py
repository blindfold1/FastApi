from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
access_token_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
refresh_token_scheme = OAuth2PasswordBearer(tokenUrl="/auth/refresh")

from fastapi import status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)