from fastapi import APIRouter

from src.api.routes.author import auth_router
from src.api.routes.clients import clients_router
from src.db.database import database_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(clients_router, prefix="/clients", tags=["Clients"])
router.include_router(database_router, prefix="/db", tags=["Database"])

__all__ = ["router"]