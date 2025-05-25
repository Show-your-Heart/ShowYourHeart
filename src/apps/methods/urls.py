from django.urls import path
from django.utils.translation import gettext_lazy as _

app_name = "methods"
urlpatterns = [
    # Topic
    path(_("topic"), name="custom_topic"),
]
