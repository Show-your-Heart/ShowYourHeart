from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import ExternalMethodFillView, MethodFillView, invitations_sent_view

app_name = "methods"
urlpatterns = [
    # Methods
    path(_("fill/<id>"), MethodFillView.as_view(), name="method_fill"),
    path(
        _("external-survey/<id>"),  # invitation.token
        ExternalMethodFillView.as_view(),
        name="external_method_fill",
    ),
    path(_("send-invitations/<id>"), invitations_sent_view, name="send_invitations"),
]
