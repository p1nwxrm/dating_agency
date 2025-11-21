from aiogram import Router

from .show_status_menu import router as status_menu_router
from .status_action import router as status_action_router

router = Router()
router.include_router(status_menu_router)
router.include_router(status_action_router)

__all__ = ["router"]