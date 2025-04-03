from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from apps.settings.models import Network, ParentNetwork
from apps.users.models import User


class Command(BaseCommand):
    help = _(
        "Fills the database with all the necessary data to make it faster "
        "for developers to work with the project when they need to "
        "re-create the database. Debug mode needs to be "
        "enabled to run this command. Make sure to set the 'Initial "
        "superuser and dev data' settings before running this command."
    )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(
                self.style.ERROR(_("This command can only be run in debug mode."))
            )
            return 0
        self.create_sample_users()
        self.create_sample_network()

    def create_sample_users(self):
        self.stdout.write(_("Creating sample users..."))

        # Superuser
        email = settings.SUPERUSER_EMAIL
        password = settings.SUPERUSER_PASSWORD
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(
                _("Superuser created with email '{email}'.").format(
                    email=email,
                )
            )
        else:
            self.stdout.write(_("Superuser already exists."))

        # Governance admin
        email = settings.USER_GOV_ADMIN_EMAIL
        password = settings.USER_GOV_ADMIN_PASSWORD
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password=password,
                name="Governace admin",
                surnames="",
                is_staff=True,
                is_active=True,
                email_verified=True,
            )
            groups = Group.objects.filter(name="Governance admins")
            user.groups.set(groups)
            self.stdout.write(
                _("Governace admin user created with email '{email}'.").format(
                    email=email,
                )
            )
        else:
            self.stdout.write(_("Governace admin user already exists."))

        return 0

    def create_sample_network(self):
        self.stdout.write(_("Creating sample network..."))
        parent_network_name = "Parent network test"
        network_name = "Network test"
        parent = ParentNetwork.objects.filter(name=parent_network_name)

        if not parent.exists():
            parent = ParentNetwork.objects.create(name=parent_network_name)
        else:
            parent = parent.first()
            self.stdout.write(_("ParentNetwork test already exists."))

        if not Network.objects.filter(name=network_name).exists():
            network_admin = User.objects.get(email=settings.SUPERUSER_EMAIL)
            Network.objects.create(
                name=network_name,
                network_admin=network_admin,
                parent_network=parent,
            )
        else:
            self.stdout.write(_("Network test already exists."))
