from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import (
    ExternalMethodFillView,
    ExternalSurveysView,
    MethodFillSuccessView,
    MethodFillView,
    MethodPreviewView,
    create_invitation_action,
    delete_invitation,
    import_csv2,
    invitation_sent_view,
    invitations_sent_view,
    load_ext_surveys,
    survey_reminder_view,
    user_survey_reminder_view,
)

app_name = "methods"
urlpatterns = [
    # Methods
    path(
        _("fill/<uuid:campaign_id>/<uuid:method_id>/"),
        MethodFillView.as_view(),
        name="method_fill",
    ),
    path(
        _("fill/success"),
        MethodFillSuccessView.as_view(),
        name="method_fill_success",
    ),
    path(
        _("external-survey/<token>"),  # invitation.token
        ExternalMethodFillView.as_view(),
        name="external_method_fill",
    ),
    path(
        _(
            "external-surveys/<uuid:organization_id>/<uuid:method_id>/<uuid:campaign_id>/"
        ),
        ExternalSurveysView.as_view(),
        name="external_surveys_view",
    ),
    path(
        _("invitation"),
        create_invitation_action,
        name="create_invitation",
    ),
    path(
        "invitations/<uuid:invitation_id>/delete/",
        delete_invitation,
        name="delete_invitation",
    ),
    path("send-invitations/<id>", invitations_sent_view, name="send_invitations"),
    path("send-invitation/<id>", invitation_sent_view, name="send_invitation"),
    path(
        "import-csv2/<uuid:organization_id>/<uuid:method_id>/<uuid:campaign_id>/",
        import_csv2,
        name="import_csv2",
    ),
    path("load_ext_surveys/", load_ext_surveys, name="load_ext_surveys"),
    # Do not translate the methods url because is used on the html templates
    path(
        "fill/<uuid:campaign_id>/<uuid:method_id>/<uuid:project_id>/",
        MethodFillView.as_view(),
        name="method_fill_project",
    ),
    path(
        _("preview/<uuid:method_id>/"),
        MethodPreviewView.as_view(),
        name="method_preview",
    ),
    path(
        "survey-reminder-send",
        survey_reminder_view,
        name="survey_reminder_email",
    ),
    path(
        "user-survey-reminder-send/<uuid:survey_id>",
        user_survey_reminder_view,
        name="user_survey_reminder_email",
    ),
]
