import environ
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from apps.users.models import User

env = environ.Env()
environ.Env.read_env()


class Command(BaseCommand):
    help = _("Fills the database with all the necessary data to make it faster "
             "for developers to work with the project when they need to "
             "re-create the database. Debug mode needs to be "
             "enabled to run this command. Make sure to set the 'Initial "
             "superuser and dev data' settings before running this command.")

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR(_(
                "This command can only be run in debug mode."
            )))
            return 0
        self.create_sample_users()

    def create_sample_users(self):
        email = env("USER_ADMIN_EMAIL")
        password = env("USER_ADMIN_PASSWORD")

        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password=password,
                name="Administrator",
                surnames="",
                is_staff=True,
                is_active=True,
            )
            groups = Group.objects.all()
            user.groups.set(groups)

        return 0
