from django.apps import AppConfig
from django.db.models.signals import post_migrate

from apps.users.signals import update_user_groups


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self):
        post_migrate.connect(update_user_groups, sender=self)
