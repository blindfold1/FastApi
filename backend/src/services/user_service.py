from ..models.user import UserCreate, UserInDB, UserResponse
from ..core.security import auth_handler
from ..db.mongodb import get_database
from fastapi import HTTPException, status
from bson import ObjectId

class UserService:
    @staticmethod
    async def create_user(user: UserCreate) -> UserResponse:
        db = await get_database()
        if await db.users.find_one({"username": user.username}):
            raise HTTPException(status_code=400, detail="Username already registered")
        if await db.users.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email already registered")
        user_dict = user.dict()
        user_dict["hashed_password"] = auth_handler.get_password_hash(user.password)
        user_dict.pop("password")
        result = await db.users.insert_one(user_dict)
        created_user = await db.users.find_one({"_id": result.inserted_id})
        return UserResponse(
            id=str(created_user["_id"]),
            username=created_user["username"],
            email=created_user["email"],
            role=created_user["role"],
            is_active=created_user["is_active"],
            is_verified=created_user.get("is_verified", False),
            created_at=created_user["created_at"],
            specialization=created_user.get("specialization"),
            experience_years=created_user.get("experience_years"),
            bio=created_user.get("bio"),
        )

    @staticmethod
    async def get_user_by_username(username: str) -> UserInDB:
        db = await get_database()
        user = await db.users.find_one({"username": username})
        if not user:
            return None
        return UserInDB(**user)

    @staticmethod
    async def get_user_by_id(user_id: str) -> UserInDB:
        db = await get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        return UserInDB(**user)

    @staticmethod
    async def get_users_by_role(role: str):
        db = await get_database()
        users = await db.users.find({"role": role}).to_list(length=100)
        return [UserResponse(
            id=str(u["_id"]),
            username=u["username"],
            email=u["email"],
            role=u["role"],
            is_active=u["is_active"],
            is_verified=u.get("is_verified", False),
            created_at=u["created_at"],
            specialization=u.get("specialization"),
            experience_years=u.get("experience_years"),
            bio=u.get("bio"),
        ) for u in users] 