"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from project.admin import gov_admin_site
from project.views import HomeView, RootRedirectView

urlpatterns = [
    path("", RootRedirectView.as_view()),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("", HomeView.as_view(), name="home"),
    path(_("registration/"), include("apps.users.urls", namespace="registration")),
    path("admin/login/", lambda request: redirect("/")),
    path("superadmin/", admin.site.urls),
    path("admin/", gov_admin_site.urls),
    path(_("settings/"), include("apps.settings.urls", namespace="settings")),
    path(
        _("organizations/"),
        include("apps.organizations.urls", namespace="organizations"),
    ),
    path(_("methods/"), include("apps.methods.urls", namespace="methods")),
)
