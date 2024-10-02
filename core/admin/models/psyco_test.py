# core/admin/models/psyco_test.py

# from fastapi import UploadFile
from sqlalchemy import select

from .base import BaseAdminModel 
from core.models.psyco_test import PsycoTest, PsycoQuestion, PsycoAnswer, PsycoQuestionAnswer, PsycoResult


class PsycoTestAdmin(BaseAdminModel, model=PsycoTest):
    column_list = ["id", "name", "description", "test_type", "is_active", "created_at", "updated_at"]
    column_details_exclude_list = ["questions", "results"]
    form_excluded_columns = ["questions", "results", "created_at", "updated_at"]
    column_searchable_list = ["name", "description", "test_type"]
    column_sortable_list = ["name", "test_type", "created_at", "updated_at"]

    category = "Psychological Tests"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoQuestionAdmin(BaseAdminModel, model=PsycoQuestion):
    column_list = ["id", "test", "question_text", "is_active", "created_at", "updated_at"]
    column_details_exclude_list = ["answer_options"]
    form_excluded_columns = ["answer_options", "created_at", "updated_at"]
    column_searchable_list = ["question_text"]
    column_sortable_list = ["created_at", "updated_at"]

    category = "Psychological Tests"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoAnswerAdmin(BaseAdminModel, model=PsycoAnswer):
    column_list = ["id", "answer_text", "is_active", "created_at", "updated_at"]
    column_searchable_list = ["answer_text"]
    column_sortable_list = ["created_at", "updated_at"]
    form_excluded_columns = ["created_at", "updated_at"]

    category = "Psychological Tests"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoQuestionAnswerAdmin(BaseAdminModel, model=PsycoQuestionAnswer):
    column_list = ["id", "question", "answer", "is_correct", "score_value", "is_active", "created_at", "updated_at"]
    column_searchable_list = ["question.question_text", "answer.answer_text"]
    column_sortable_list = ["created_at", "updated_at", "is_correct", "score_value"]
    form_excluded_columns = ["created_at", "updated_at"]

    category = "Psychological Tests"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query


class PsycoResultAdmin(BaseAdminModel, model=PsycoResult):
    column_list = ["id", "test", "min_score", "max_score", "text", "is_active", "created_at", "updated_at"]
    column_searchable_list = ["text"]
    column_sortable_list = ["min_score", "max_score", "created_at", "updated_at"]
    form_excluded_columns = ["created_at", "updated_at"]

    category = "Psychological Tests"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query
