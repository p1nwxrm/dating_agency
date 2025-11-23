from aiogram import Router

from .users import router as users_router
from .admins import router as admins_router
from .moderators import router as moderators_router

from .common.start import router as start_router
from .common.info import router as info_router
from .common.fallback import router as fallback_router

router = Router()

router.include_router(start_router)
router.include_router(info_router)

router.include_router(users_router)
router.include_router(admins_router)
router.include_router(moderators_router)

router.include_router(fallback_router)

__all__ = ["router"]