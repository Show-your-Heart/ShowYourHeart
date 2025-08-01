from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import MethodFillView

app_name = "methods"
urlpatterns = [
    # Methods
    path(_("fill/<id>"), MethodFillView.as_view(), name="method_fill"),
]
