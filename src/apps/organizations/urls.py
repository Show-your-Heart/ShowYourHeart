from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.organizations.views import CreateOrganizationView, load_methods

app_name = "organizations"
urlpatterns = [
    # Organizations
    path(_("sign-up/"), CreateOrganizationView.as_view(), name="signup"),
    path(_("sign-up/load_methods/"), load_methods, name="load_methods"),
]
