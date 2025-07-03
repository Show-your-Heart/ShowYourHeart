from django.contrib.auth.decorators import login_not_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView

from apps.organizations.forms import OrganizationSignUpForm

from .models import Organization


@method_decorator(login_not_required, name="dispatch")
class CreateOrganizationView(CreateView):
    model = Organization
    template_name = "organizations/signup.html"
    form_class = OrganizationSignUpForm
