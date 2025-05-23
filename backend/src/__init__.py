"""
Blog Platform Source Code
"""

from fastapi import APIRouter
from .api.routes import auth_router, articles_router

router = APIRouter()

router.include_router(auth_router, tags=["Authentication"])
router.include_router(articles_router, tags=["Articles"])

__all__ = ["router"]
