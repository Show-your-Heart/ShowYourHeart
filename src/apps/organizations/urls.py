from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.organizations.views import (
    CreateOrganizationSuccessView,
    CreateOrganizationView,
    CreateProjectSuccessView,
    CreateProjectView,
    UpdateOrganizationView,
    load_methods,
)

app_name = "organizations"
urlpatterns = [
    # Organizations
    path(_("sign-up/"), CreateOrganizationView.as_view(), name="signup"),
    path(
        _("sign-up/success"),
        CreateOrganizationSuccessView.as_view(),
        name="signup_success",
    ),
    path(_("sign-up/load_methods/"), load_methods, name="load_methods"),
    path(_("update/<pk>"), UpdateOrganizationView.as_view(), name="update"),
    path(
        _("<uuid:organization_id>/project/"),
        CreateProjectView.as_view(),
        name="create_project",
    ),
    path(
        _("project/success"),
        CreateProjectSuccessView.as_view(),
        name="create_project_success",
    ),
]
