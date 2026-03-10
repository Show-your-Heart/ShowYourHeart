from django.apps import apps


def get_smtp_for_user(user):
    """
    Return the SMTPServer for a specific network.
    Must explicitly pass a network, since user can have more than one.
    """
    SMTPServer = apps.get_model("settings", "SMTPServer")

    user_networks = user.profile.organization.networks.all()

    smtp = SMTPServer.objects.filter(network__in=user_networks).first()

    return smtp
