from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from import_export import resources
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from apps.methods.models import Method
from apps.settings.models import Network
from apps.users.models import UserProfile
from apps.users.services import (
    send_rejected_mail,
    send_welcome_mail,
)
from project.admin import ImportExportModelAdmin, ModelAdmin, gov_admin_site
from project.decorators import gov_admin_register, register_with_default_templates
from project.mixins import NetworkFilterMixin

from .forms import OrganizationAdminExportForm, OrganizationAdminForm
from .helpers import filter_methods_by_legal_structure
from .models import Organization, Project
from .views import RegistrationRequestView


class OrganizationResource(resources.ModelResource):
    def __init__(self, **kwargs):
        super().__init__()
        self.region1_id = kwargs.get("region1_id")

    def filter_export(self, queryset, **kwargs):
        return queryset.filter(region1_id=self.region1_id)

    class Meta:
        model = Organization
        # fields = ('id', 'name', 'price',)


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Organization)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Organization)
class OrganizationAdmin(NetworkFilterMixin, ImportExportModelAdmin):
    form = OrganizationAdminForm
    list_display = ("name", "status", "resolution_date")
    filter_horizontal = ("methods",)
    readonly_fields = ("contact", "resolution_date", "network")
    list_filter = [("status", ChoicesDropdownFilter)]
    autocomplete_fields = ["country", "region1", "city", "sectors"]
    search_fields = ["name"]

    resource_classes = [OrganizationResource]
    export_form_class = OrganizationAdminExportForm

    def get_export_resource_kwargs(self, request, **kwargs):
        export_form = kwargs.get("export_form")
        if export_form:
            kwargs.update(region1_id=export_form.cleaned_data["region1"].id)
        return kwargs

    def get_fieldsets(self, request, obj=None):
        # Do not display "log fields" twice, display them only on a "Log" section
        log_fields = [
            "created_by",
            "created_at",
            "updated_at",
            "privacy_policy_accepted",
        ]
        default_fields = super().get_fieldsets(request, obj)

        fieldsets = self.build_fieldsets(
            main_fields=[
                f for f in default_fields[0][1]["fields"] if f not in log_fields
            ],
        )

        if self.is_legal_structure_readonly(obj):
            # When the field is set as readonly is placed at the bottom of the list
            # Replace it on his original place
            fieldsets[0][1]["fields"].remove("legal_structure")
            fieldsets[0][1]["fields"].insert(
                len(fieldsets[0][1]["fields"]) - 3, "legal_structure"
            )

        fieldsets[0][1]["fields"].remove("contact")
        fieldsets[0][1]["fields"].insert(2, "contact")
        fieldsets[0][1]["fields"].remove("resolution_date")
        fieldsets[0][1]["fields"].insert(10, "resolution_date")

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if self.is_legal_structure_readonly(obj):
            readonly_fields += ("legal_structure",)
        return readonly_fields

    def is_legal_structure_readonly(self, obj):
        # Set the legal structure field as readonly
        # if the organization has already mehtods
        if obj and obj.methods.exists():
            return True
        else:
            return False

    def get_form(self, request, obj=None, **kwargs):
        # Add legal_structure property to use it on formfield_for_manytomany
        if obj:
            self.legal_structure_id = obj.legal_structure.id
        return super().get_form(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Display only the corresponding methods
        if db_field.name == "methods":
            if hasattr(self, "legal_structure_id"):
                qs = Method.objects.all()
                kwargs["queryset"] = filter_methods_by_legal_structure(
                    qs, self.legal_structure_id
                )
            else:
                kwargs["queryset"] = Method.objects.none()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def contact(self, obj):
        user_profile = UserProfile.objects.filter(organization=obj)
        if user_profile:
            return (
                user_profile.first().user.email
                + " ("
                + user_profile.first().user.name
                + ")"
            )
        else:
            return "-"

    def network(self, obj):
        network = Network.objects.filter(organizations__id__contains=obj.id)
        if network:
            return network.first().name
        else:
            return "-"

    # Add custom urls
    def get_urls(self):
        urls = [
            path(
                "registration-requests",
                self.admin_site.admin_view(
                    RegistrationRequestView.as_view(model_admin=self)
                ),
                name="registration_requests",
            ),
            path(
                "registration-request-action/<uuid:pk>/",
                self.admin_site.admin_view(
                    self.register_request_action,
                ),
                name="register_request_actions",
            ),
        ] + super().get_urls()
        return urls

    @method_decorator(require_POST)
    def register_request_action(self, request, pk):
        organization = get_object_or_404(Organization, pk=pk)
        action = request.POST.get("action")
        profile = UserProfile.objects.filter(organization=organization).first()
        if action == "accept":
            organization.status = Organization.Status.ACCEPTED
            organization.save()
            send_welcome_mail(profile.user)
        elif action == "reject":
            organization.status = Organization.Status.REJECTED
            organization.save()
            send_rejected_mail(profile.user)

        return HttpResponse("")


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Project)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Project)
class ProjectAdmin(NetworkFilterMixin, ModelAdmin):
    list_display = (
        "name",
        "organization",
    )
    filter_horizontal = ("methods",)
    autocomplete_fields = ["region1", "city"]
    search_fields = ["name", "organization"]
    organization_field = "organization"

    def get_fieldsets(self, request, obj=None):
        # Do not display "log fields" twice, display them only on a "Log" section
        log_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]
        default_fields = super().get_fieldsets(request, obj)

        fieldsets = self.build_fieldsets(
            main_fields=[
                f for f in default_fields[0][1]["fields"] if f not in log_fields
            ],
        )
        return fieldsets
