import environ
from django.core.management.base import BaseCommand

from apps.users.models import User

env = environ.Env()
environ.Env.read_env()


class Command(BaseCommand):
    help = "Crea el superuser predeterminat sempre que no existeixi ja."

    def handle(self, *args, **options):
        email = env("DJANGO_SUPERUSER_EMAIL")
        password = env("DJANGO_SUPERUSER_PASSWORD")

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, password=password)

        return 0
