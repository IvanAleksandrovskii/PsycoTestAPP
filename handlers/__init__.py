from aiogram import Router
from .on_start import router as on_start_router
from .movie_quiz import router as movie_quiz_router

router = Router()
router.include_router(on_start_router)
router.include_router(movie_quiz_router)

__all__ = [
    "router",
]
