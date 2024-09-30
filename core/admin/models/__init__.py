__all__ = [
    "setup_admin",
]

from .tg_user import TgUserAdmin

# Register admin views
def setup_admin(admin):
    admin.add_view(TgUserAdmin)
