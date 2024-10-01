__all__ = [
    "setup_admin",
]

from .tg_user import TgUserAdmin
from .movie_quiz import MovieQuizAdmin, MovieQuizQuestionAdmin, MovieQuizAnswerAdmin


# Register admin views
def setup_admin(admin):
    admin.add_view(TgUserAdmin)
    admin.add_view(MovieQuizAdmin)
    admin.add_view(MovieQuizQuestionAdmin)
    admin.add_view(MovieQuizAnswerAdmin)
