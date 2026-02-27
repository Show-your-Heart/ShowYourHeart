from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import (
    ExternalMethodFillView,
    ExternalSurveysView,
    MethodFillView,
    MethodPreviewView,
    create_invitation_action,
    import_csv,
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
        _("external-survey/<token>"),  # invitation.token
        ExternalMethodFillView.as_view(),
        name="external_method_fill",
    ),
    path(
        _("external-surveys/<uuid:organization_id>/<uuid:method_id>/"),
        ExternalSurveysView.as_view(),
        name="external_surveys_view",
    ),
    path(
        _("invitation"),
        create_invitation_action,
        name="create_invitation",
    ),
    path(_("send-invitations/<id>"), invitations_sent_view, name="send_invitations"),
    path(_("send-invitation/<id>"), invitation_sent_view, name="send_invitation"),
    path(_("import-csv/<id>"), import_csv, name="import_csv"),
    path(
        _("import-csv2/<uuid:organization_id>/<uuid:method_id>"),
        import_csv2,
        name="import_csv2",
    ),
    path(_("load_ext_surveys/"), load_ext_surveys, name="load_ext_surveys"),
    path(
        _("fill/<uuid:campaign_id>/<uuid:method_id>/<uuid:project_id>/"),
        MethodFillView.as_view(),
        name="method_fill_project",
    ),
    path(
        _("preview/<uuid:method_id>/"),
        MethodPreviewView.as_view(),
        name="method_preview",
    ),
    path(
        _("survey-reminder-send"),
        survey_reminder_view,
        name="survey_reminder_email",
    ),
    path(
        _("user-survey-reminder-send/<uuid:survey_id>"),
        user_survey_reminder_view,
        name="user_survey_reminder_email",
    ),
]
