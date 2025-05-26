from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "project"

    def ready(self):
        # Monkey-patch to adapt post_office models to Unfold version 0.57
        from post_office.admin import AttachmentInline, EmailTemplateInline

        EmailTemplateInline.ordering_field = ("",)
        AttachmentInline.ordering_field = ("",)
