from aiogram import Router

from .name import router as name_router
from .age import router as age_router
from .gender import router as gender_router
from .goal import router as goal_router
from .desired_genders import router as desired_genders_router
from .location import router as location_router
from .search_radius import router as search_radius_router
from .photo import router as photo_router
from .about import router as about_router
from .save_profile import router as save_profile_router

router = Router()
router.include_router(name_router)
router.include_router(age_router)
router.include_router(gender_router)
router.include_router(goal_router)
router.include_router(desired_genders_router)
router.include_router(location_router)
router.include_router(search_radius_router)
router.include_router(photo_router)
router.include_router(about_router)
router.include_router(save_profile_router)

__all__ = ["router"]