# core/admin/models/psyco_test_with_correct_answer.py

from typing import Any
from fastapi import UploadFile
from sqlalchemy import select

from .base import BaseAdminModel
from core.models.psyco_test_with_correct_answer import (
    PycoTestWithCorrectAnswer,
    PsycoQuestionWithCorrectAnswer,
    PsycoAnswerWithCorrectMarker,
    PsycoResultWithFromToGroup
)


class PycoTestWithCorrectAnswerAdmin(BaseAdminModel, model=PycoTestWithCorrectAnswer):
    column_list = ["id", "name", "description", "is_active", "created_at", "updated_at"]
    column_details_exclude_list = ["questions", "results"]
    form_excluded_columns = ["questions", "results", "created_at", "updated_at"]
    column_searchable_list = ["name", "description"]
    column_sortable_list = ["name", "created_at", "updated_at"]

    category = "Psychological Test With Correct Answer"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoQuestionWithCorrectAnswerAdmin(BaseAdminModel, model=PsycoQuestionWithCorrectAnswer):
    column_list = ["id", "test", "question_text", "is_active", "created_at", "updated_at"]
    column_details_exclude_list = ["answers"]
    form_excluded_columns = ["answers", "created_at", "updated_at"]
    column_searchable_list = ["question_text"]
    column_sortable_list = ["created_at", "updated_at"]

    category = "Psychological Test With Correct Answer"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoAnswerWithCorrectMarkerAdmin(BaseAdminModel, model=PsycoAnswerWithCorrectMarker):
    column_list = ["id", "question", "answer_text", "is_correct", "is_active", "created_at", "updated_at"]
    column_searchable_list = ["answer_text"]
    column_sortable_list = ["created_at", "updated_at", "is_correct"]
    form_excluded_columns = ["created_at", "updated_at"]

    category = "Psychological Test With Correct Answer"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoResultWithFromToGroupAdmin(BaseAdminModel, model=PsycoResultWithFromToGroup):
    column_list = ["id", "test", "min_score", "max_score", "text", "is_active", "created_at", "updated_at"]
    column_searchable_list = ["text"]
    column_sortable_list = ["min_score", "max_score", "created_at", "updated_at"]
    form_excluded_columns = ["created_at", "updated_at"]

    category = "Psychological Test With Correct Answer"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query
