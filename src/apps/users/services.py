from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
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


def send_welcome_mail(user_instance):
    password_reset_url = absolute_url(
        reverse(
            "registration:password_reset_confirm",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(user_instance.pk)),
                "token": default_token_generator.make_token(user_instance),
            },
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
        "absolute_url": settings.ABSOLUTE_URL,
        "password_reset_url": password_reset_url,
    }
    send(
        recipients=[
            user_instance.email,
        ],
        template="welcome",
        context=context,
    )


def send_rejected_mail(user_instance):
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
    }
    send(
        recipients=[
            user_instance.email,
        ],
        template="rejected_registration_request",
        context=context,
    )


def send_network_assigned_mail(network_instance):
    context = {
        "project_name": Setting.get("PROJECT_NAME"),
        "user_name": network_instance.network_admin.name,
        "date": str(
            formats.date_format(
                timezone.now().date(),
                format="SHORT_DATE_FORMAT",
                use_l10n=True,
            )
        ),
        "time": str(formats.time_format(timezone.localtime(timezone.now()).time())),
        "network_name": network_instance.name,
    }

    send(
        recipients=[
            network_instance.network_admin.email,
        ],
        template="network_assigned",
        context=context,
    )
