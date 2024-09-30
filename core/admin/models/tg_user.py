from core.admin.models.base import BaseAdminModel
from core.models.tg_user import TGUser


class TgUserAdmin(BaseAdminModel, model=TGUser):
    column_list = [TGUser.id, TGUser.chat_id, TGUser.username, TGUser.is_superuser, TGUser.created_at, TGUser.updated_at]
    column_searchable_list = [TGUser.id, TGUser.chat_id, TGUser.username]
    column_sortable_list = [TGUser.id, TGUser.chat_id, TGUser.is_superuser, TGUser.username, TGUser.username, TGUser.created_at, TGUser.updated_at]
    column_filters = [TGUser.chat_id, TGUser.username, TGUser.is_superuser]
    column_details_list = [TGUser.id, TGUser.chat_id, TGUser.username, TGUser.is_superuser, TGUser.created_at, TGUser.updated_at]
    can_create = False
    can_edit = True
    can_delete = True
    name = "Telegram User"
    name_plural = "Telegram Users"
    category = "Telegram"
