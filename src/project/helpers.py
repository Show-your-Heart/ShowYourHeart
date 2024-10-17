from django.conf import settings


def absolute_url(path):
    return f"{settings.ABSOLUTE_URL}{path}"
