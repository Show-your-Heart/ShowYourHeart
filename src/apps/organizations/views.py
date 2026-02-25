from django.contrib.auth.decorators import login_not_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from unfold.views import UnfoldModelAdminViewMixin

from apps.geodata.models import City, Region1, ZipCode
from apps.methods.models import Method
from apps.organizations.forms import (
    OrganizationSignUpForm,
    OrganizationUpdateForm,
)
from project.mixins import NetworkFilterMixin

from .helpers import filter_methods_by_legal_structure, get_methods_for_region1
from .models import Organization, Project


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
    methods = Method.objects.none()
    legal_structure_id = request.GET.get("legal_structure")
    region1_id = request.GET.get("region1")

    if region1_id:
        methods = get_methods_for_region1(region1_id)

    if legal_structure_id:
        methods = filter_methods_by_legal_structure(methods, legal_structure_id)
    return render(request, "organizations/methods_options.html", {"methods": methods})


@method_decorator(login_not_required, name="dispatch")
@require_http_methods("GET")
def load_region1(request):
    regions = Region1.objects.none()
    if country_id := request.GET.get("country"):
        regions = Region1.objects.filter(country_id=country_id).order_by("name")

    return render(
        request,
        "organizations/region1_options.html",
        {"regions": regions},
    )


@method_decorator(login_not_required, name="dispatch")
@require_http_methods("GET")
def load_city(request):
    cities = City.objects.none()
    if region1_id := request.GET.get("region1"):
        cities = City.objects.filter(region1_id=region1_id).order_by("name")

    return render(
        request,
        "organizations/city_options.html",
        {"cities": cities},
    )


@method_decorator(login_not_required, name="dispatch")
@require_http_methods("GET")
def load_zip_code(request):
    zip_codes = ZipCode.objects.none()
    if city_id := request.GET.get("city"):
        zip_codes = ZipCode.objects.filter(city_id=city_id).order_by("code")

    return render(
        request,
        "organizations/zip_code_options.html",
        {"zip_codes": zip_codes},
    )


@method_decorator(login_not_required)
@require_http_methods("POST")
def create_project_action(request, organization_id):
    project, created = Project.objects.get_or_create(
        organization_id=organization_id,
        name=request.POST["name"],
        description=request.POST["description"],
        start_date=request.POST["start_date"],
        contact_name=request.POST["contact_name"],
        contact_email=request.POST["contact_email"],
        contact_telephone=request.POST["contact_telephone"],
        main_action_scope=request.POST["main_action_scope"],
        secondary_action_scope=request.POST["secondary_action_scope"],
        main_legal_entity_type=request.POST["main_legal_entity_type"],
        secondary_legal_entity_type=request.POST["secondary_legal_entity_type"],
        authorize=request.POST["authorize"] == "on",
        publish_results=request.POST["publish_results"] == "on",
    )
    if created:
        method_id = request.POST.get("method_id")
        method = Method.objects.get(pk=method_id)
        campaign = method.campaign_methods.filter(status=True).first()
        return HttpResponse(
            "",
            headers={
                "HX-Redirect": f"/methods/fill/{campaign.id}/{request.POST['method_id']}/{project.id}",  # noqa: E501
            },
        )
    else:
        msg = _("Error creating project. Contact your network admin.")
        return HttpResponse(
            "",
            headers={
                "HX-Retarget": "#notifications",
                "HX-Reswap": "beforeend",
                "HX-Trigger": '{"notification": {"type": "error","text": "'
                + msg
                + '"}}',
            },
        )


################
# Custom views #
################


class RegistrationRequestView(
    UnfoldModelAdminViewMixin, TemplateView, NetworkFilterMixin
):
    title = "Registration requests"
    permission_required = ()
    template_name = "admin/organizations/registration_requests.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        organizations = Organization.objects.all().filter(
            status=Organization.Status.PENDING
        )
        if "q" in self.request.GET:
            query_filter = self.request.GET["q"]
            organizations = organizations.filter(name__contains=query_filter)
            context["query_filter"] = query_filter

        organizations = self.filter_queryset_by_network(self.request, organizations)

        context["organizations"] = organizations
        return context
