from aiogram import Router

from .edit_profile import router as edit_router
from .mutual_likes import router as mutual_likes_router
from .profile_stat import router as stat_router

router = Router()
router.include_router(edit_router)
router.include_router(mutual_likes_router)
router.include_router(stat_router)

__all__ = ["router"]