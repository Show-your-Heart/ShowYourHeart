from django.contrib.auth.decorators import login_not_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from unfold.views import UnfoldModelAdminViewMixin

from apps.methods.models import Method
from apps.organizations.forms import (
    OrganizationSignUpForm,
    OrganizationUpdateForm,
    ProjectCreationForm,
    ProjectSelectionForm,
)

from .helpers import get_organization_method_filter
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
    if legal_structure_id := request.GET.get("legal_structure"):
        try:
            methods = get_organization_method_filter(legal_structure_id)
        except Method.DoesNotExist:
            methods = []
    else:
        methods = []
    return render(request, "organizations/methods_options.html", {"methods": methods})


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
        return HttpResponse(
            "",
            headers={
                "HX-Redirect": f"/methods/{request.POST['method_id']}/fill/{project.id}",
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


class RegistrationRequestView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Registration requests"
    permission_required = ()
    template_name = "admin/organizations/registration_requests.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if "q" in self.request.GET:
            query_filter = self.request.GET["q"]
            context["organizations"] = Organization.objects.filter(
                name__contains=query_filter
            ).exclude(status=Organization.Status.ACCEPTED)
            context["query_filter"] = self.request.GET["q"]
        else:
            context["organizations"] = Organization.objects.all().exclude(
                status=Organization.Status.ACCEPTED
            )
        return context


class CreateProjectView(CreateView):
    model = Project
    template_name = "projects/create_project.html"
    form_class = ProjectCreationForm
    success_url = reverse_lazy("organizations:create_project_success")

    def dispatch(self, request, *args, **kwargs):
        self.organization = request.user.profile.organization
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        return kwargs

    def form_valid(self, form):
        project = form.save(commit=False)
        project.organization = self.organization
        project.save()
        return super().form_valid(form)


class CreateProjectSuccessView(TemplateView):
    template_name = "projects/create_project_success.html"


class ChooseProjectView(FormView):
    template_name = "components/modals/choose_project.html"
    form_class = ProjectSelectionForm

    def dispatch(self, request, *args, **kwargs):
        self.organization = request.user.profile.organization
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        return kwargs

    def get_form(self):
        form = super().get_form()
        form.fields["project"].queryset = Project.objects.filter(
            organization=self.request.user.profile.organization
        )
        return form
