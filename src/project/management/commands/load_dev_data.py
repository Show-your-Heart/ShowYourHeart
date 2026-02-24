import random
import string

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.geodata.models import (
    City,
    Country,
    Region1,
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
    REGION1_NAME = "Galicia"
    CITY_NAME = "Pontevedra"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(
                self.style.ERROR(_("This command can only be run in debug mode."))
            )
            return 0

        legal_structure = self.create_legal_structure()
        country = self.create_sample_country()
        region1 = self.create_sample_region1()
        city = self.create_sample_city()
        network = self.create_sample_network()
        topics = self.create_sample_topics()
        indicators = self.create_sample_indicators(topics)
        methods = self.create_sample_methods(legal_structure, indicators, network)
        self.create_sample_campaign(methods)
        self.create_sample_users(legal_structure, country, region1, city, methods)

    def create_sample_users(self, legal_structure, country, region1, city, methods):
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
            legal_structure, country, region1, city, methods
        )

        return 0

    def create_sample_network(self):
        self.stdout.write(_("Creating sample network..."))
        network_name = "Network test"
        network_type = "Network type"
        network = Network.objects.filter(name=network_name)

        if not network.exists():
            network = Network.objects.create(
                name=network_name,
                network_type=network_type,
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
        self, legal_structure, country, region1, city, methods
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
                user, legal_structure, country, region1, city, methods
            )

            user.user_profile = UserProfile.objects.create(
                user=user, organization=organizations[0]
            )
            user.save()
        else:
            self.stdout.write(_("Governace admin user already exists."))

        # Test user
        email = settings.USER_EMAIL
        password = settings.USER_PASSWORD
        if not User.objects.filter(email=email).exists():
            user = User.objects.create(
                email=email,
                password=password,
                name="User",
                surnames="",
                is_staff=False,
                is_active=True,
                email_verified=True,
            )
            self.stdout.write(
                _("User created with email '{email}'.").format(
                    email=email,
                )
            )

            user.user_profile = UserProfile.objects.create(
                user=user, organization=(Organization.objects.filter().all())[1]
            )
            user.save()
        else:
            self.stdout.write(_("User already exists."))

    def create_sample_organizations(
        self, user, legal_structure, country, region1, city, methods
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
                    region1=region1,
                    city=city,
                    status=1,
                    legal_structure=legal_structure,
                    resolution_date=timezone.now(),
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
            indicator_name = f"Indicator name q000{x}"
            indicator = Indicator.objects.filter(name=indicator_name)
            if not indicator.exists():
                indicator = Indicator.objects.create(
                    code=f"q000{x}",
                    version="1",
                    name=indicator_name,
                    is_direct_indicator=True,
                    unit="K",
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
            method_qs = Method.objects.filter(name=method_name)
            if not method_qs.exists():
                method = Method.objects.create(
                    name=method_name,
                    description=f"Method description {x}",
                )
                method.indicators.set(indicators)
                method.legal_structures.set([legal_structures])
                (method.networks.set([network]),)
            else:
                method = method_qs.first()
                self.stdout.write(_(f"{method_name} already exists."))
            methods.append(method)
        return methods

    def create_sample_country(self):
        self.stdout.write(_("Creating sample country..."))
        country_qs = Country.objects.filter(name=self.COUNTRY_NAME)

        if not country_qs.exists():
            country = Country.objects.create(
                name=self.COUNTRY_NAME,
            )
        else:
            self.stdout.write(_("Country already exists."))
            country = country_qs.first()

        return country

    def create_sample_city(self):
        self.stdout.write(_("Creating sample city..."))
        city_qs = City.objects.filter(name=self.CITY_NAME)

        if not city_qs.exists():
            city = City.objects.create(
                name=self.CITY_NAME,
                country=self.create_sample_country(),
                region1=self.create_sample_region1(),
            )
        else:
            self.stdout.write(_("City already exists."))
            city = city_qs.first()

        return city

    def create_sample_region1(self):
        self.stdout.write(_("Creating sample Region1..."))
        region1_qs = Region1.objects.filter(name=self.REGION1_NAME)

        if not region1_qs.exists():
            region1 = Region1.objects.create(
                name=self.REGION1_NAME,
                country=self.create_sample_country(),
            )
        else:
            self.stdout.write(_("Region1 already exists."))
            region1 = region1_qs.first()
        return region1

    def create_sample_campaign(self, methods):
        self.stdout.write(_("Creating sample Campaign..."))
        campaigns = []
        campaign_name = "2025"
        campaign_qs = Campaign.objects.filter(name=campaign_name)

        if not campaign_qs.exists():
            campaign = Campaign.objects.create(
                name=campaign_name,
                year=campaign_name,
                status=1,
            )
            campaign.methods.set(methods)
        else:
            self.stdout.write(_("Campaign already exists."))
            campaign = campaign_qs.first()

        campaigns.append(campaign)

        return campaign
