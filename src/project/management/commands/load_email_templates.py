import logging

from django.apps import apps
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from project.post_office import textify


class Command(BaseCommand):
    help = _("Fills the database with all the default email templates. ")

    def handle(self, *args, **options):
        self.populate_mail_templates()

    def populate_mail_templates(self):
        mail_model = apps.get_model("post_office", "EmailTemplate")

        templates = [
            dict(
                id="password_reset",
                translated_templates={
                    "en": {
                        "subject": (
                            "Password reset for your account at {{project_name}}"
                        ),
                        "body": open(
                            "./templates/emails/en/password_reset.html"
                        ).read(),
                    },
                    "ca": {
                        "subject": "Reinicialització de contrasenya del teu compte a "
                        "{{project_name}}",
                        "body": open(
                            "./templates/emails/ca/password_reset.html"
                        ).read(),
                    },
                },
            ),
            dict(
                id="email_verification",
                translated_templates={
                    "en": {
                        "subject": "Email verification code for your account at "
                        "{{project_name}}",
                        "body": open(
                            "./templates/emails/en/email_verification.html"
                        ).read(),
                    },
                    "ca": {
                        "subject": (
                            "Verificació del correu electrònic a {{project_name}}"
                        ),
                        "body": open(
                            "./templates/emails/ca/email_verification.html"
                        ).read(),
                    },
                },
            ),
            dict(
                id="network_assigned",
                translated_templates={
                    "en": {
                        "subject": "Network assigned on {{project_name}}",
                        "body": open(
                            "./templates/emails/en/network_assigned.html"
                        ).read(),
                    },
                },
            ),
            dict(
                id="welcome",
                translated_templates={
                    "en": {
                        "subject": "Activated account on {{project_name}}",
                        "body": open("./templates/emails/en/welcome.html").read(),
                    },
                },
            ),
            dict(
                id="rejected_registration_request",
                translated_templates={
                    "en": {
                        "subject": "Rejected registration request on {{project_name}}",
                        "body": open(
                            "./templates/emails/en/rejected_registration_request.html",
                        ).read(),
                    }
                },
            ),
            dict(
                id="external_survey_invitation",
                translated_templates={
                    "en": {
                        "subject": "Invitation to {{method_name}}",
                        "body": open(
                            "./templates/emails/en/external_survey_invitation.html",
                        ).read(),
                    },
                },
            ),
        ]

        for template in templates:
            obj, created = mail_model.objects.update_or_create(
                name=template.get("id"),
                defaults={
                    "name": template.get("id"),
                },
            )
            for lang, translated_template in template.get(
                "translated_templates"
            ).items():
                obj.translated_templates.create(
                    language=lang,
                    subject=translated_template.get("subject"),
                    html_content=translated_template.get("body"),
                    content=textify(translated_template.get("body")),
                    # name field included due this bug:
                    # https://github.com/ui/django-post_office/issues/214
                    name=template.get("id"),
                )
                logging.info(f"E-mail template '{template.get('id')}' created.")
