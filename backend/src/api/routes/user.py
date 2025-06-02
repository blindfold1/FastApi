from fastapi import APIRouter, Depends, HTTPException, status
from ...models.user import UserCreate, UserResponse
from ...services.user_service import UserService
from ...core.security import auth_handler
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ...core.config import settings
from bson import ObjectId, errors as bson_errors
from ...db.mongodb import get_database

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    user.role = "user"
    return await UserService.create_user(user)

@router.post("/register_trainer", response_model=UserResponse)
async def register_trainer(user: UserCreate):
    user.role = "trainer"
    return await UserService.create_user(user)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserService.get_user_by_username(form_data.username)
    if not user or not auth_handler.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth_handler.create_access_token(
        {"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(auth_handler.get_current_user)):
    user = await UserService.get_user_by_id(current_user["_id"])
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        specialization=user.specialization,
        experience_years=user.experience_years,
        bio=user.bio,
    )

@router.get("/trainers", response_model=list[UserResponse])
async def get_trainers():
    return await UserService.get_users_by_role("trainer")

@router.get("/", response_model=list[UserResponse])
async def get_users():
    return await UserService.get_users_by_role("user")

@router.get("/admins", response_model=list[UserResponse])
async def get_admins():
    return await UserService.get_users_by_role("admin")

@router.post("/make_admin/{username}")
async def make_admin(username: str, current_user=Depends(auth_handler.get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can assign admin role")
    user = await UserService.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db = await get_database()
    await db.users.update_one({"username": username}, {"$set": {"role": "admin"}})
    return {"message": f"User {username} is now admin"}

def validate_object_id(oid: str):
    try:
        return ObjectId(oid)
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format") 