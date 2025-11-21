from aiogram import Router

from .blacklist import router as blacklist_router
from .others import router as others_router
from .profile_status import router as profile_status_router
from .rating import router as rating_router
from .registration import router as registration_router

router = Router()
router.include_router(blacklist_router)
router.include_router(others_router)
router.include_router(profile_status_router)
router.include_router(rating_router)
router.include_router(registration_router)

__all__ = ["router"]