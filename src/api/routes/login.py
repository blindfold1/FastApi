

from fastapi import security,Depends, HTTPException,APIRouter

from sqlalchemy import select
from starlette.responses import JSONResponse

from src.api.auth.token import OAuth2PasswordBearer, decode_access_token, create_access_token
from src.api.dependencies import SessionDep, pwd_context

from src.config import logger
from src.models.model import Users
from src.pydantic_models import User_Credentials

login_router = APIRouter(prefix="/auth", tags=["Auth"])


@login_router.post("/login")
async def login(creds: User_Credentials, session: SessionDep):
    try:
        result = await session.execute(select(Users).where(Users.username == creds.username))
        user = result.scalars().first()
        if not user or not pwd_context.verify(creds.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect credentials")

        token = create_access_token(subject=str(user.id))
        return {"Login successful":token, "token_type": "bearer"}
    except Exception as login_error:
        logger.error(f"Wrong credentials: {login_error}")
        raise HTTPException(status_code=500, detail="Internal server error")

@login_router.get("/protected")
async def protected(token : str = Depends(OAuth2PasswordBearer)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message":"You have access","user":payload["sub"]}


