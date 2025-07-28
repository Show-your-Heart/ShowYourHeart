from django.contrib.auth.decorators import login_not_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView

from apps.methods.models import Method
from apps.organizations.forms import OrganizationSignUpForm

from .models import Organization


@method_decorator(login_not_required, name="dispatch")
class CreateOrganizationView(CreateView):
    model = Organization
    template_name = "organizations/signup.html"
    form_class = OrganizationSignUpForm


@method_decorator(login_not_required, name="dispatch")
@require_http_methods("GET")
def load_methods(request):
    legal_structure_id = request.GET.get("legal_structure")
    methods = Method.objects.filter(legal_structures__id=legal_structure_id)
    return render(request, "organizations/methods_options.html", {"methods": methods})
