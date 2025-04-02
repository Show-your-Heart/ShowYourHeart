from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.settings.views import admin_assigned_view

app_name = "settings"
urlpatterns = [
    # Settings
    path(_("admin-assigned/<id>"), admin_assigned_view, name="admin_assigned"),
]
