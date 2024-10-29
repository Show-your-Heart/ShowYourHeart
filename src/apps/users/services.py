from django.conf import settings
from django.urls import reverse
from django.utils import formats, timezone
from extra_settings.models import Setting

from apps.users.utils import email_verification_code_regeneration
from project.helpers import absolute_url
from project.post_office import send


def send_confirmation_mail(user_instance):
    email_verification_code = email_verification_code_regeneration(user_instance)
    email_verification_url = absolute_url(
        reverse(
            "registration:user_validation",
        )
    )
    context = {
        "project_name": Setting.get("PROJECT_NAME"),
        "user_name": user_instance.name,
        "date": str(
            formats.date_format(
                timezone.now().date(),
                format="SHORT_DATE_FORMAT",
                use_l10n=True,
            )
        ),
        "time": str(formats.time_format(timezone.localtime(timezone.now()).time())),
        "user_email": user_instance.email,
        "user_code": email_verification_code,
        "absolute_url": settings.ABSOLUTE_URL,
        "email_verification_url": email_verification_url,
    }
    send(
        recipients=[
            user_instance.email,
        ],
        template="email_verification",
        context=context,
    )
