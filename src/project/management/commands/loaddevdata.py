import random
import string

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext as _

from apps.geodata.models import (
    City,
    Country,
    Region,
)
from apps.methods.models import Campaign, Indicator, Method, Topic
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
    COUNTRY_NAME = "Spain"
    REGION_NAME = "Galicia"
    CITY_NAME = "Pontevedra"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(
                self.style.ERROR(_("This command can only be run in debug mode."))
            )
            return 0

        legal_structure = self.create_legal_structure()
        country = self.create_sample_country()
        region = self.create_sample_region()
        city = self.create_sample_city()
        network = self.create_sample_network()
        topics = self.create_sample_topics()
        indicators = self.create_sample_indicators(topics)
        methods = self.create_sample_methods(legal_structure, indicators, network)
        self.create_sample_campaign()
        self.create_sample_users(legal_structure, country, region, city, methods)

    def create_sample_users(self, legal_structure, country, region, city, methods):
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

        self.create_users_with_organization(
            legal_structure, country, region, city, methods
        )

        return 0

    def create_sample_network(self):
        self.stdout.write(_("Creating sample network..."))
        network_name = "Network test"
        network = Network.objects.filter(name=network_name)

        if not network.exists():
            network_admin = User.objects.get(email=settings.SUPERUSER_EMAIL)
            network = Network.objects.create(
                name=network_name,
                network_admin=network_admin,
            )
        else:
            self.stdout.write(_("Network test already exists."))
            network = network[0]

        return network

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
    def create_users_with_organization(
        self, legal_structure, country, region, city, methods
    ):
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

            organizations = self.create_sample_organizations(
                user, legal_structure, country, region, city, methods
            )

            user.user_profile = UserProfile.objects.create(
                user=user, organization=organizations[0]
            )
            user.save()
        else:
            self.stdout.write(_("Governace admin user already exists."))

    def create_sample_organizations(
        self, user, legal_structure, country, region, city, methods
    ):
        organizations = []
        self.stdout.write(_("Creating sample organizations..."))

        for org_name in self.ORGANIZATION_NAMES:
            if not Organization.objects.filter(name=org_name).exists():
                org = Organization.objects.create(
                    name=org_name,
                    vat_number="".join(
                        random.choices(string.ascii_uppercase + string.digits, k=10)
                    ),
                    country=country,
                    region=region,
                    city=city,
                    contact=user,
                    status=1,
                    legal_structure=legal_structure,
                )
                org.methods.set(methods)
                organizations.append(org)

        return organizations

    def create_sample_topics(self):
        self.stdout.write(_("Creating sample topics..."))
        topic_list = []

        for x in range(1, 4):
            topic_name = "topic" + str(x)
            topic_filter = Topic.objects.filter(name=topic_name)
            if not topic_filter.exists():
                topic = Topic.objects.create(
                    name=topic_name, description=f"description for {topic_name}"
                )
                topic_list.append(topic)
            else:
                self.stdout.write(_(f"{topic_name} already exists."))
                for queryset in topic_filter:
                    topic_list.append(queryset)

        return topic_list

    @transaction.atomic
    def create_sample_indicators(self, topics):
        self.stdout.write(_("Creating sample indicators..."))
        indicators = []

        for x in range(1, 4):
            indicator_name = f"Indicator name {x}"
            indicator = Indicator.objects.filter(name=indicator_name)
            if not indicator.exists():
                indicator = Indicator.objects.create(
                    project_id=x,
                    version="1",
                    name=indicator_name,
                    is_direct_indicator=True,
                )
                indicator.topics.set(topics)
            else:
                self.stdout.write(_(f"{indicator_name} already exists."))
                indicator = indicator[0]
            indicators.append(indicator)
        return indicators

    def create_sample_methods(self, legal_structures, indicators, network):
        self.stdout.write(_("Creating sample methods..."))
        methods = []

        for x in range(1, 4):
            method_name = f"Method name {x}"
            method = Method.objects.filter(name=method_name)
            if not method.exists():
                method = Method.objects.create(
                    name=method_name,
                    description=f"Method description {x}",
                    active=True,
                    network_owner=network,
                )
                method.indicators.set(indicators)
                method.legal_structures.set([legal_structures])
            else:
                self.stdout.write(_(f"{method_name} already exists."))
            methods.append(method)
        return method

    def create_sample_country(self):
        self.stdout.write(_("Creating sample country..."))
        country_filter = Country.objects.filter(name=self.COUNTRY_NAME)

        if not country_filter.exists():
            country = Country.objects.create(
                name=self.COUNTRY_NAME,
            )
        else:
            self.stdout.write(_("Country already exists."))
            country = country_filter[0]

        return country

    def create_sample_city(self):
        self.stdout.write(_("Creating sample city..."))
        city_filter = City.objects.filter(name=self.CITY_NAME)

        if not city_filter.exists():
            city = City.objects.create(
                name=self.CITY_NAME,
            )
        else:
            self.stdout.write(_("City already exists."))
            city = city_filter[0]

        return city

    def create_sample_region(self):
        self.stdout.write(_("Creating sample Region..."))
        region_filter = Region.objects.filter(name=self.REGION_NAME)

        if not region_filter.exists():
            region = Region.objects.create(
                name=self.REGION_NAME,
            )
        else:
            self.stdout.write(_("Region already exists."))
            region = region_filter[0]

        return region

    def create_sample_campaign(self):
        self.stdout.write(_("Creating sample Campaign..."))
        campaign_name = "2025"
        campaign_filter = Campaign.objects.filter(name=campaign_name)

        if not campaign_filter.exists():
            campaign = Campaign.objects.create(
                name=campaign_name,
                year=campaign_name,
                status=1,
            )
        else:
            self.stdout.write(_("Campaign already exists."))
            campaign = campaign_filter[0]

        return campaign
