__all__ = [
    "setup_admin",
]

from .tg_user import TgUserAdmin
from .movie_quiz import MovieQuizAdmin, MovieQuizQuestionAdmin, MovieQuizAnswerAdmin
from .psyco_test_with_correct_answer import (
    PycoTestWithCorrectAnswerAdmin, PsycoQuestionWithCorrectAnswerAdmin,
    PsycoAnswerWithCorrectMarkerAdmin, PsycoResultWithFromToGroupAdmin
)


# Register admin views
def setup_admin(admin):
    admin.add_view(TgUserAdmin)
    admin.add_view(MovieQuizAdmin)
    admin.add_view(MovieQuizQuestionAdmin)
    admin.add_view(MovieQuizAnswerAdmin)
    admin.add_view(PycoTestWithCorrectAnswerAdmin)
    admin.add_view(PsycoQuestionWithCorrectAnswerAdmin)
    admin.add_view(PsycoAnswerWithCorrectMarkerAdmin)
    admin.add_view(PsycoResultWithFromToGroupAdmin)
