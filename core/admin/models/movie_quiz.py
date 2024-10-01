# core/admin/models/movie_quiz.py

from typing import Any
from fastapi import UploadFile
from sqladmin import ModelView
from sqlalchemy import select

from .base import BaseAdminModel
from core.models import MovieQuiz, MovieQuizQuestion, MovieQuizAnswer
from services import movie_quiz_storage


class MovieQuizAdmin(BaseAdminModel, model=MovieQuiz):
    column_list = ["id", "title", "description", "is_active", "created_at", "updated_at"]
    column_details_exclude_list = ["questions"]
    form_excluded_columns = ["questions", "created_at", "updated_at"]
    column_searchable_list = ["title", "description"]
    column_sortable_list = ["title", "created_at", "updated_at"]

    category = "Movie Quiz"

    async def on_model_change(self, data: dict, model: Any, is_created: bool, session: Any) -> None:
        if "picture" in data and isinstance(data["picture"], UploadFile):
            filename = await movie_quiz_storage.put(data["picture"])
            model.picture = filename
    
    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class MovieQuizQuestionAdmin(BaseAdminModel, model=MovieQuizQuestion):
    column_list = ["id", "quiz", "question_text", "interesting_fact", "picture", "is_active", "created_at", "updated_at"]
    column_details_exclude_list = ["answers"]
    form_excluded_columns = ["answers", "created_at", "updated_at"]
    column_searchable_list = ["question_text", "interesting_fact"]
    column_sortable_list = ["created_at", "updated_at"]

    category = "Movie Quiz"

    async def on_model_change(self, data: dict, model: Any, is_created: bool, session: Any) -> None:
        if "picture" in data and isinstance(data["picture"], UploadFile):
            filename = await movie_quiz_storage.put(data["picture"])
            model.picture = filename

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class MovieQuizAnswerAdmin(BaseAdminModel, model=MovieQuizAnswer):
    column_list = ["id", "question", "answer_text", "is_correct", "is_active", "created_at", "updated_at"]
    column_searchable_list = ["answer_text"]
    column_sortable_list = ["created_at", "updated_at", "is_correct"]
    form_excluded_columns = ["created_at", "updated_at"]

    category = "Movie Quiz"

    
    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query
