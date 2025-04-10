from fastapi import APIRouter

from .api.routes import auth_router, clients_router, food_router
from .db import database_router

router = APIRouter()

router.include_router(auth_router, tags=["Authentication"])
router.include_router(clients_router, tags=["clients"])
router.include_router(food_router, tags=["food"])
router.include_router(database_router, tags=["database"])

__all__ = ["router"]
