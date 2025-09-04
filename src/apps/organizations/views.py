from django.contrib.auth.decorators import login_not_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from apps.methods.models import Method
from apps.organizations.forms import OrganizationSignUpForm

from .helpers import get_organization_method_filter
from .models import Organization


@method_decorator(login_not_required, name="dispatch")
class CreateOrganizationView(CreateView):
    model = Organization
    template_name = "organizations/signup.html"
    form_class = OrganizationSignUpForm
    success_url = reverse_lazy("organizations:signup_success")


@method_decorator(login_not_required, name="dispatch")
class CreateOrganizationSuccessView(TemplateView):
    template_name = "organizations/signup_success.html"


class UpdateOrganizationView(UpdateView):
    model = Organization
    template_name = "organizations/signup.html"
    success_url = "/"
    form_class = OrganizationUpdateForm


@method_decorator(login_not_required, name="dispatch")
@require_http_methods("GET")
def load_methods(request):
    if legal_structure_id := request.GET.get("legal_structure"):
        try:
            methods = get_organization_method_filter(legal_structure_id)
        except Method.DoesNotExist:
            methods = []
    else:
        methods = []
    return render(request, "organizations/methods_options.html", {"methods": methods})
