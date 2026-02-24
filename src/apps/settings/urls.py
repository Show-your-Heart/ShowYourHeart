from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.settings.views import (
    ContactView,
    DocumentsView,
    GoodPracticesView,
    ResourcesView,
    WhatIsSocialBalanceView,
)

app_name = "settings"
urlpatterns = [
    # Settings
    path(
        _("what-is-social-balance"),
        WhatIsSocialBalanceView.as_view(),
        name="what_is_social_balance",
    ),
    path(_("good-practices"), GoodPracticesView.as_view(), name="good_practices"),
    path(_("documents"), DocumentsView.as_view(), name="documents"),
    path(_("resources"), ResourcesView.as_view(), name="resources"),
    path(_("contact"), ContactView.as_view(), name="contact"),
]
