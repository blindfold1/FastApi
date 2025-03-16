from fastapi import APIRouter
from .clients import clients_router
from .login import login_router
from .credentials import credentials_router
from src.api.auth.token import auth_router  # Исправлен импорт
from src.models.database import database_router

router = APIRouter()

# Убираем дублирование префиксов
router.include_router(clients_router)
router.include_router(login_router)
router.include_router(credentials_router)
router.include_router(auth_router)

router.include_router(database_router)

__all__ = ["router"]