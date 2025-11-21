from aiogram import Router

from .complaints import router as complaints_router
from .rate import router as rate_router
from .viewing import router as viewing_router

router = Router()
router.include_router(complaints_router)
router.include_router(rate_router)
router.include_router(viewing_router)

__all__ = ["router"]