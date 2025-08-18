from django.conf import settings

from project.post_office import send


def send_invitation(invitation):
    context = {
        "method_name": "",
        "user_name": invitation.name,
        "method_url": settings.ABSOLUTE_URL
        + "/methods/external-survey/"
        + invitation.token,
    }
    send(
        recipients=[
            invitation.email,
        ],
        template="external_survey_invitation",
        context=context,
    )
