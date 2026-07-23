from django.urls import reverse

from project.post_office import send
from project.utils.smtp_utils import get_from_email, get_smtp_for_user

from .models import Survey


def send_invitation(request, invitation):
    method_url = request.build_absolute_uri(
        reverse("methods:external_method_fill", args=[invitation.token])
    )

    context = {
        "method_name": invitation.external_survey_invitation.name,
        "entity_name": invitation.external_survey_invitation.organization.name,
        "user_name": invitation.name,
        "method_url": method_url,
    }

    smtp = get_smtp_for_user(user=request.user)
    from_email = get_from_email(user=request.user)

    send(
        sender=from_email,
        recipients=[invitation.email],
        template="external_survey_invitation",
        context=context,
        smtp=smtp,
    )


def send_survey_reminder_email(request):
    user_emails = []
    surveys = Survey.objects.filter(status=Survey.Status.OPEN).all()
    for survey in surveys:
        if survey.user.email not in user_emails:
            user_emails.append(survey.user.email)

    smtp = get_smtp_for_user(user=request.user)
    from_email = get_from_email(user=request.user)
    send(
        sender=from_email,
        bcc=user_emails,
        template="survey_reminder",
        smtp=smtp,
    )


def send_user_survey_reminder_email(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    context = {"user_name": survey.user.name, "survey": survey.method.name}

    smtp = get_smtp_for_user(user=request.user)
    from_email = get_from_email(user=request.user)
    send(
        sender=from_email,
        recipients=[survey.user.email],
        template="user_survey_reminder",
        context=context,
        smtp=smtp,
    )


def send_survey_status_update_email(request, survey_id, survey_status):
    template = None
    if survey_status == Survey.Status.TECH_VALIDATED:
        template = "survey_tech_validated"
    elif survey_status == Survey.Status.QUALITY_CHECKED:
        template = "survey_quality_checked"

    if template:
        survey = Survey.objects.get(id=survey_id)
        context = {"user_name": survey.user.name, "method_name": survey.method.name}

        smtp = get_smtp_for_user(user=request.user)
        from_email = get_from_email(user=request.user)
        return send(
            sender=from_email,
            recipients=[survey.user.email],
            template=template,
            context=context,
            smtp=smtp,
        )
    else:
        return ""  # The survey status is not configured to send an email
