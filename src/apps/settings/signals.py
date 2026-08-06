from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def register_sites(sender, **kwargs):
    expected_sites = getattr(settings, "EXPECTED_SITES", None)
    if not expected_sites:
        return

    for domain, name in expected_sites:
        Site.objects.update_or_create(domain=domain, defaults={"name": name})
