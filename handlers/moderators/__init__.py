from aiogram import Router

from .ban import router as ban_router
from .stat import router as stats_router

router = Router()
router.include_router(ban_router)
router.include_router(stats_router)

__all__ = ["router"]