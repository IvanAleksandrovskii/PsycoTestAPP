__all__ = [
    "setup_admin",
]

from .tg_user import TgUserAdmin
from .movie_quiz import MovieQuizAdmin, MovieQuizQuestionAdmin, MovieQuizAnswerAdmin
from .psyco_test import PsycoTestAdmin, PsycoResultAdmin, PsycoQuestionAdmin, PsycoQuestionAnswerAdmin, PsycoAnswerAdmin


# Register admin views
def setup_admin(admin):
    admin.add_view(TgUserAdmin)
    admin.add_view(MovieQuizAdmin)
    admin.add_view(MovieQuizQuestionAdmin)
    admin.add_view(MovieQuizAnswerAdmin)
    admin.add_view(PsycoTestAdmin)
    admin.add_view(PsycoResultAdmin)
    admin.add_view(PsycoQuestionAdmin)
    admin.add_view(PsycoQuestionAnswerAdmin)
    admin.add_view(PsycoAnswerAdmin)
