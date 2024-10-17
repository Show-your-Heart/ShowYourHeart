from django.conf import settings
from django.db import migrations
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password

from django.utils import timezone


def generate_superuser(apps, schema_editor):
    user_model = apps.get_model("users.User")

    email = settings.DJANGO_SUPERUSER_EMAIL
    password = settings.DJANGO_SUPERUSER_PASSWORD

    if not email or not password:
        print(
            "\nSkipping initial superuser creation. Set "
            "DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD "
            "environment variables to enable it.\n"
        )
        return

    user = user_model()
    user.email = BaseUserManager.normalize_email(email)
    user.password = make_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_validated = timezone.now()
    user.save()

    print("\n\tInitial superuser created.")


def remove_superuser(apps, schema_editor):
    try:
        user_model = apps.get_model("users.User")
        superuser = user_model.objects.filter(email=settings.DJANGO_SUPERUSER_EMAIL)

        if superuser.exists():
            superuser.delete()
            print("\nInitial superuser removed.\n")

    except Exception as error:
        raise error


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [migrations.RunPython(generate_superuser, remove_superuser)]
