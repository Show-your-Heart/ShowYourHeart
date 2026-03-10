import re

from django.apps import apps
from django.core.mail import EmailMessage, get_connection
from django.utils.html import strip_tags
from django.utils.translation import get_language
from post_office import mail as base_mail


def send(
    recipients=None,
    sender=None,
    template=None,
    context=None,
    subject="",
    message="",
    html_message="",
    scheduled_time=None,
    expires_at=None,
    headers=None,
    priority=None,
    attachments=None,
    render_on_delivery=False,
    log_level=None,
    commit=True,
    cc=None,
    bcc=None,
    language="",
    backend="",
    smtp=None,
):
    if not language:
        language = get_language()

    template_mail_model = apps.get_model("post_office", "EmailTemplate")
    template_exists = template_mail_model.objects.filter(
        name=template, language=language
    ).exists()

    if not template_exists:
        # Set English as the template language
        language = "en"

    print("SMTPPPPPPPPPPPPP")
    print(smtp, smtp.host, smtp.port)
    if smtp:
        connection = get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=smtp.host,
            port=smtp.port,
            username=smtp.username,
            password=smtp.password,
            use_tls=(smtp.protocol == "TLS"),
            use_ssl=(smtp.protocol == "SSL"),
        )

        email = EmailMessage(
            subject=subject,
            body=template,
            from_email=sender,
            to=recipients,
            cc=cc,
            bcc=bcc,
            headers=headers,
            connection=connection,
        )
        print(email)
        return email.send()

    # Otherwise use Post Office as before
    return base_mail.send(
        recipients=recipients,
        sender=sender,
        template=template,
        context=context,
        subject=subject,
        message=message,
        html_message=html_message,
        scheduled_time=scheduled_time,
        expires_at=expires_at,
        headers=headers,
        priority=priority,
        attachments=attachments,
        render_on_delivery=render_on_delivery,
        log_level=log_level,
        commit=commit,
        cc=cc,
        bcc=bcc,
        language=language,
        backend=backend,
    )


def textify(html):
    # Remove html tags and continuous whitespaces
    text_only = re.sub("[ \t]+", " ", strip_tags(html))
    # Strip single spaces in the beginning of each line
    return text_only.replace("\n ", "\n").strip()
