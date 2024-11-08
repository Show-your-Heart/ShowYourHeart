import logging

from django.conf import settings
from django.db import migrations
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext as _

from django.utils import timezone


logging.basicConfig(level=logging.INFO)


def generate_superuser(apps, schema_editor):
    user_model = apps.get_model("users.User")

    email = settings.SUPERUSER_EMAIL
    password = settings.SUPERUSER_PASSWORD

    if not email or not password:
        logging.info(
            _(
                "Skipping initial superuser creation. Set "
                "SUPERUSER_EMAIL and SUPERUSER_PASSWORD "
                "environment variables to enable it."
            )
        )
        return

    user = user_model()
    user.email = BaseUserManager.normalize_email(email)
    user.password = make_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_validated = timezone.now()
    user.save()

    logging.info("Initial superuser created.")


def remove_superuser(apps, schema_editor):
    try:
        user_model = apps.get_model("users.User")
        superuser = user_model.objects.filter(email=settings.SUPERUSER_EMAIL)

        if superuser.exists():
            superuser.delete()
            logging.info("Initial superuser removed.")

    except Exception as error:
        raise error


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [migrations.RunPython(generate_superuser, remove_superuser)]
