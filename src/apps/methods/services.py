from django.conf import settings

from project.post_office import send

from .models import Survey


def send_invitation(invitation):
    context = {
        "method_name": invitation.external_survey_invitation.name,
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


def send_survey_reminder_email():
    user_emails = []
    surveys = Survey.objects.filter(status=Survey.Status.OPEN).all()
    for survey in surveys:
        if survey.user.email not in user_emails:
            user_emails.append(survey.user.email)

    send(
        recipients=user_emails,
        template="survey_reminder",
    )
