from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.organizations.views import CreateOrganizationView

app_name = "organizations"
urlpatterns = [
    # Organizations
    path(_("sign-up/"), CreateOrganizationView.as_view(), name="signup"),
]
