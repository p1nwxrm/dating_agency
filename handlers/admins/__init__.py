from aiogram import Router

from .staff_stats import router as staff_stats_router
from .user_stats import router as user_stats_router

router = Router()
router.include_router(staff_stats_router)
router.include_router(user_stats_router)

__all__ = ["router"]