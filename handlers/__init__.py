from aiogram import Router
from .on_start import router as on_start_router
from .movie_quiz import router as movie_quiz_router
from .admin import router as admin_router
from .psyco_tests import router as psyco_tests_router
from .send_test import router as send_test_router

router = Router()
router.include_router(on_start_router)
router.include_router(movie_quiz_router)
router.include_router(admin_router)
router.include_router(psyco_tests_router)
router.include_router(send_test_router)

__all__ = [
    "router",
]
