import logging

from django.apps import apps
from django.core.management.base import BaseCommand

from project.post_office import textify


class Command(BaseCommand):
    help = "Fills the database with all the default email templates. "

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
                id="welcome",
                translated_templates={
                    "en": {
                        "subject": "Activated account on {{project_name}}",
                        "body": open("./templates/emails/en/welcome.html").read(),
                    },
                    "es": {
                        "subject": "Cuenta activada en {{project_name}}",
                        "body": open("./templates/emails/es/welcome.html").read(),
                    },
                    "eu": {
                        "subject": "Cuenta activada en {{project_name}}",
                        "body": open("./templates/emails/eu/welcome.html").read(),
                    },
                    "ca": {
                        "subject": "Cuenta activada en {{project_name}}",
                        "body": open("./templates/emails/ca/welcome.html").read(),
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
                    },
                    "es": {
                        "subject": "Solicitud de acceso rechazada en {{project_name}}",
                        "body": open(
                            "./templates/emails/es/rejected_registration_request.html",
                        ).read(),
                    },
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
                    "es": {
                        "subject": "Invitación a {{method_name}}",
                        "body": open(
                            "./templates/emails/es/external_survey_invitation.html",
                        ).read(),
                    },
                },
            ),
            dict(
                id="survey_reminder",
                translated_templates={
                    "en": {
                        "subject": "Remainder to finish your current survey",
                        "body": open(
                            "./templates/emails/en/survey_reminder.html",
                        ).read(),
                    },
                },
            ),
            dict(
                id="user_survey_reminder",
                translated_templates={
                    "en": {
                        "subject": "Remainder to finish your current survey",
                        "body": open(
                            "./templates/emails/en/user_survey_reminder.html",
                        ).read(),
                    },
                },
            ),
            dict(
                id="survey_tech_validated",
                translated_templates={
                    "en": {
                        "subject": "Survey status updated to tech validated",
                        "body": open(
                            "./templates/emails/en/survey_tech_validated.html",
                        ).read(),
                    },
                },
            ),
            dict(
                id="survey_quality_checked",
                translated_templates={
                    "en": {
                        "subject": "Survey status updated to quality checked",
                        "body": open(
                            "./templates/emails/en/survey_quality_checked.html",
                        ).read(),
                    },
                },
            ),
            dict(
                id="registration",
                translated_templates={
                    "en": {
                        "subject": "Register request",
                        "body": open(
                            "./templates/emails/en/registration.html",
                        ).read(),
                    },
                    "es": {
                        "subject": "Solicitud de registro",
                        "body": open(
                            "./templates/emails/es/registration.html",
                        ).read(),
                    },
                },
            ),
        ]

        for template in templates:
            existing_templates = mail_model.objects.filter(
                name=template.get("id")
            ).all()

            if not existing_templates:
                obj, created = mail_model.objects.update_or_create(
                    name=template.get("id"),
                    language="",
                    defaults={
                        "name": template.get("id"),
                    },
                )
            else:
                obj = existing_templates.first()

            for lang, translated_template in template.get(
                "translated_templates"
            ).items():
                obj.translated_templates.update_or_create(
                    # name field included due this bug:
                    # https://github.com/ui/django-post_office/issues/214
                    name=template.get("id"),
                    language=lang,
                    defaults={
                        "subject": translated_template.get("subject"),
                        "html_content": translated_template.get("body"),
                        "content": textify(translated_template.get("body")),
                    },
                )
                logging.info(f"E-mail template '{template.get('id')}-{lang}' created.")
