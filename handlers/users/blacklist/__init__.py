from aiogram import Router

from .viewing import router as view_blacklist_router
from .toggle_block import router as toggle_block_router

router = Router()
router.include_router(view_blacklist_router)
router.include_router(toggle_block_router)

__all__ = ["router"]