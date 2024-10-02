# core/admin/models/psyco_test_with_score_answers.py

from typing import Any
from fastapi import UploadFile
from sqlalchemy import select

from .base import BaseAdminModel
from core.models.psyco_tests_with_score_answers import (
    PsycoTestWithScoreAnswers,
    PsycoQuestionWithScoreAnswers,
    PsycoAnswerWithScoreMarker,
    PsycoResultWithScoreGroup
)


class PsycoTestWithScoreAnswersAdmin(BaseAdminModel, model=PsycoTestWithScoreAnswers):
    column_list = ["id", "name", "description", "is_active", "created_at", "updated_at"]
    column_details_exclude_list = ["questions", "results"]
    form_excluded_columns = ["questions", "results", "created_at", "updated_at"]
    column_searchable_list = ["name", "description"]
    column_sortable_list = ["name", "created_at", "updated_at"]

    category = "Psychological Test With Score Answers"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoQuestionWithScoreAnswersAdmin(BaseAdminModel, model=PsycoQuestionWithScoreAnswers):
    column_list = ["id", "test", "question_text", "is_active", "created_at", "updated_at"]
    column_details_exclude_list = ["answers"]
    form_excluded_columns = ["answers", "created_at", "updated_at"]
    column_searchable_list = ["question_text"]
    column_sortable_list = ["created_at", "updated_at"]

    category = "Psychological Test With Score Answers"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoAnswerWithScoreMarkerAdmin(BaseAdminModel, model=PsycoAnswerWithScoreMarker):
    column_list = ["id", "question", "answer_text", "score_value", "is_active", "created_at", "updated_at"]
    column_searchable_list = ["answer_text"]
    column_sortable_list = ["created_at", "updated_at", "score_value"]
    form_excluded_columns = ["created_at", "updated_at"]

    category = "Psychological Test With Score Answers"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoResultWithScoreGroupAdmin(BaseAdminModel, model=PsycoResultWithScoreGroup):
    column_list = ["id", "test", "min_score", "max_score", "text", "is_active", "created_at", "updated_at"]
    column_searchable_list = ["text"]
    column_sortable_list = ["min_score", "max_score", "created_at", "updated_at"]
    form_excluded_columns = ["created_at", "updated_at"]

    category = "Psychological Test With Score Answers"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query
