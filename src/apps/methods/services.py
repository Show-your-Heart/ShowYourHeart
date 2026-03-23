from django.urls import reverse

from project.post_office import send
from project.utils.smtp_utils import get_smtp_for_user

from .models import Survey


def send_invitation(request, invitation):
    method_url = request.build_absolute_uri(
        reverse("methods:external_method_fill", args=[invitation.token])
    )

    context = {
        "method_name": invitation.external_survey_invitation.name,
        "user_name": invitation.name,
        "method_url": method_url,
    }

    smtp = get_smtp_for_user(user=request.user)

    send(
        recipients=[invitation.email],
        template="external_survey_invitation",
        context=context,
        smtp=smtp,
    )


def send_survey_reminder_email():
    user_emails = []
    surveys = Survey.objects.filter(status=Survey.Status.OPEN).all()
    for survey in surveys:
        if survey.user.email not in user_emails:
            user_emails.append(survey.user.email)

    send(
        bcc=user_emails,
        template="survey_reminder",
    )


def send_user_survey_reminder_email(survey_id):
    survey = Survey.objects.get(id=survey_id)
    context = {"user_name": survey.user.name, "survey": survey.method.name}
    send(
        recipients=[survey.user.email],
        template="user_survey_reminder",
        context=context,
    )
