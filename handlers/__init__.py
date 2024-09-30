from aiogram import Router
from .on_start import router as on_start_router

router = Router()
router.include_router(on_start_router)

__all__ = [
    "router",
]
