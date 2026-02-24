from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.organizations.views import (
    CreateOrganizationSuccessView,
    CreateOrganizationView,
    UpdateOrganizationView,
    create_project_action,
    load_city,
    load_methods,
    load_region1,
    load_zip_code,
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
    path(_("sign-up/load_region1/"), load_region1, name="load_region1"),
    path(_("sign-up/load_city/"), load_city, name="load_city"),
    path(_("sign-up/load_zip_code/"), load_zip_code, name="load_zip_code"),
    path(_("update/<pk>"), UpdateOrganizationView.as_view(), name="update"),
    path(
        _("<uuid:organization_id>/project/"),
        create_project_action,
        name="create_project",
    ),
]
