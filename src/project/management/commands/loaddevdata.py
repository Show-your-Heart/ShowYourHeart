import random
import string

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext as _

from apps.methods.models import Topic
from apps.organizations.models import Organization
from apps.settings.models import LegalStructure, Network
from apps.users.models import User, UserProfile


class Command(BaseCommand):
    help = _(
        "Fills the database with all the necessary data to make it faster "
        "for developers to work with the project when they need to "
        "re-create the database. Debug mode needs to be "
        "enabled to run this command. Make sure to set the 'Initial "
        "superuser and dev data' settings before running this command."
    )
    ORGANIZATION_NAMES = ["Organization TEST", "Organization TEST2"]
    LEGAL_STRUCTURE_NAME = "LegalStructure test"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(
                self.style.ERROR(_("This command can only be run in debug mode."))
            )
            return 0

        legal_structure = self.create_legal_structure()
        self.create_sample_users(legal_structure)
        self.create_sample_network()
        self.create_sample_topics()

    def create_sample_users(self, legal_structure):
        self.stdout.write(_("Creating sample users..."))

        # Superuser
        email = settings.SUPERUSER_EMAIL
        password = settings.SUPERUSER_PASSWORD
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email, password=password, name="Superuser"
            )
            self.stdout.write(
                _("Superuser created with email '{email}'.").format(
                    email=email,
                )
            )
        else:
            self.stdout.write(_("Superuser already exists."))

        self.create_users_with_organization(legal_structure)

        return 0

    def create_sample_network(self):
        self.stdout.write(_("Creating sample network..."))
        network_name = "Network test"

        if not Network.objects.filter(name=network_name).exists():
            network_admin = User.objects.get(email=settings.SUPERUSER_EMAIL)
            Network.objects.create(
                name=network_name,
                network_admin=network_admin,
            )
        else:
            self.stdout.write(_("Network test already exists."))

    def create_legal_structure(self):
        legal_structure = {}
        self.stdout.write(_("Creating sample legal structure..."))
        legal_structure_filter = LegalStructure.objects.filter(
            name=self.LEGAL_STRUCTURE_NAME
        )

        if not legal_structure_filter.exists():
            legal_structure = LegalStructure.objects.create(
                name=self.LEGAL_STRUCTURE_NAME,
            )
        else:
            self.stdout.write(_("LegalStructure test already exists."))
            legal_structure = legal_structure_filter[0]

        return legal_structure

    @transaction.atomic
    def create_users_with_organization(self, legal_structure):
        # Governance admin
        email = settings.USER_GOV_ADMIN_EMAIL
        password = settings.USER_GOV_ADMIN_PASSWORD
        if not User.objects.filter(email=email).exists():
            user = User.objects.create(
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

            organizations = self.create_sample_organizations(user, legal_structure)

            user.user_profile = UserProfile.objects.create(
                user=user, organization=organizations[0]
            )
            user.save()
        else:
            self.stdout.write(_("Governace admin user already exists."))

    def create_sample_organizations(self, user, legal_structure):
        organizations = []
        self.stdout.write(_("Creating sample organizations..."))

        for org_name in self.ORGANIZATION_NAMES:
            if not Organization.objects.filter(name=org_name).exists():
                org = Organization.objects.create(
                    name=org_name,
                    vat_number="".join(
                        random.choices(string.ascii_uppercase + string.digits, k=10)
                    ),
                    contact=user,
                    country="Spain",
                    region="Galicia",
                    city="Pontevedra",
                    status=1,
                    legal_structure=legal_structure,
                )
                organizations.append(org)

        return organizations

    def create_sample_topics(self):
        self.stdout.write(_("Creating sample topics..."))

        for x in range(1, 4):
            topic_name = "topic" + str(x)
            if not Topic.objects.filter(name=topic_name).exists():
                Topic.objects.create(
                    name=topic_name, description=f"description for {topic_name}"
                )
            else:
                self.stdout.write(_(f"{topic_name} already exists."))
