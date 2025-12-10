from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.organizations.views import ChooseProjectView

from .views import (
    ExternalMethodFillView,
    MethodFillView,
    import_csv,
    invitation_sent_view,
    invitations_sent_view,
    load_ext_surveys,
)

app_name = "methods"
urlpatterns = [
    # Methods
    path(
        _("fill/<campaign_id>/<id>"),
        MethodFillView.as_view(),
        name="method_fill",
    ),
    path(
        _("fill/<id>"),
        MethodFillView.as_view(),
        name="method_fill",
    ),
    path(
        _("external-survey/<id>"),  # invitation.token
        ExternalMethodFillView.as_view(),
        name="external_method_fill",
    ),
    path(_("send-invitations/<id>"), invitations_sent_view, name="send_invitations"),
    path(_("send-invitation/<id>"), invitation_sent_view, name="send_invitation"),
    path(_("import-csv/<id>"), import_csv, name="import_csv"),
    path(_("load_ext_surveys/"), load_ext_surveys, name="load_ext_surveys"),
    path(_("choose_project/"), ChooseProjectView.as_view(), name="choose_project"),
    path(
        _("<uuid:id>/fill/<uuid:project_id>/"),
        MethodFillView.as_view(),
        name="method_fill_project",
    ),
]
