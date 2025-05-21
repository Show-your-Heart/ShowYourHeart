from django.views.generic.edit import CreateView

from apps.organizations.forms import OrganizationSignUpForm

from .models import Organization


class CreateOrganizationView(CreateView):
    model = Organization
    template_name = "organizations/signup.html"
    form_class = OrganizationSignUpForm
