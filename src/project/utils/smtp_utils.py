from django.apps import apps
from django.conf import settings


def get_smtp_for_user(user):
    """
    Return the SMTPServer for a specific network.
    Must explicitly pass a network, since user can have more than one.
    """
    SMTPServer = apps.get_model("settings", "SMTPServer")

    user_networks = user.profile.organization.networks.all()

    smtp = SMTPServer.objects.filter(network__in=user_networks).first()

    return smtp


def get_from_email(user):
    smtp = get_smtp_for_user(user)

    from_email = smtp.from_email if smtp else settings.DEFAULT_FROM_EMAIL

    return from_email
