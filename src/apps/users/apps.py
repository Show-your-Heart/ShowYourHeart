from django.apps import AppConfig
from django.db.models.signals import post_delete, post_migrate

from apps.users.signals import delete_user_when_profile_deleted, update_user_groups


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self):
        post_migrate.connect(update_user_groups, sender=self)
        post_delete.connect(
            delete_user_when_profile_deleted, sender="users.UserProfile"
        )
