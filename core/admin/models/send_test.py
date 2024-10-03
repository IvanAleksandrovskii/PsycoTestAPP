# core/admin/models/send_test.py

# from sqladmin import ModelView
from .base import BaseAdminModel
from sqlalchemy import select
from core.models import SentTest, TGUser, PsycoTest

class SendTestAdmin(BaseAdminModel, model=SentTest):
    column_list = [
        "sender_id", "receiver", "receiver_username", "test", "is_completed", 
        "created_at", "is_delivered", "delivered_at", "completed_at", "is_active"
    ]
    column_details_list = "__all__"
    form_excluded_columns = ["id", "created_at", "updated_at", "completed_at", "is_delivered", "delivered_at"]
    column_searchable_list = ["receiver_username", "sender_id", "receiver.username", "test.name"]
    column_sortable_list = [
        "created_at", "is_delivered", "delivered_at", "completed_at", 
        "is_active", "receiver_username", "is_completed"
    ]
    column_filters = ["is_completed", "is_delivered", "is_active", "test.name"]

    # column_labels = {
    #     "sender": "Отправитель",
    #     "receiver": "Получатель",
    #     "receiver_username": "Имя получателя",
    #     "test": "Тест",
    #     "is_completed": "Завершен",
    #     "created_at": "Создан",
    #     "is_delivered": "Доставлен",
    #     "delivered_at": "Время доставки",
    #     "completed_at": "Время завершения",
    #     "is_active": "Активен"
    # }

    # column_formatters = {
    #     "sender": lambda m, a: m.sender.username if m.sender else "N/A",
    #     "receiver": lambda m, a: m.receiver.username if m.receiver else "N/A",
    #     "test": lambda m, a: m.test.name if m.test else "N/A"
    # }

    # form_ajax_refs = {
    #     "sender": {
    #         "fields": ("username",),
    #         "model": TGUser
    #     },
    #     "receiver": {
    #         "fields": ("username",),
    #         "model": TGUser
    #     },
    #     "test": {
    #         "fields": ("name",),
    #         "model": PsycoTest
    #     }
    # }

    category = "Управление тестами"
    # name = "Отправленные тесты"
    icon = "fa-solid fa-paper-plane"

    async def scaffold_list_query(self):
        query = select(self.model).order_by(self.model.created_at.desc())
        return query
