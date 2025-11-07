from django.contrib import admin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from apps.methods.models import Method
from apps.users.models import UserProfile
from project.admin import ModelAdmin, gov_admin_site
from project.decorators import gov_admin_register, register_with_default_templates

from .forms import OrganizationAdminForm
from .helpers import get_organization_method_filter
from .models import Organization, Project


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Organization)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Organization)
class OrganizationAdmin(ModelAdmin):
    form = OrganizationAdminForm
    list_display = (
        "name",
        "status",
    )
    filter_horizontal = ("methods",)
    readonly_fields = ("contact",)
    list_filter = [("status", ChoicesDropdownFilter)]
    autocomplete_fields = ["country", "region3", "city"]
    search_fields = ["name"]

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
                len(fieldsets[0][1]["fields"]) - 2, "legal_structure"
            )

        fieldsets[0][1]["fields"].remove("contact")
        fieldsets[0][1]["fields"].insert(2, "contact")
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
                kwargs["queryset"] = get_organization_method_filter(
                    self.legal_structure_id
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


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Project)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Project)
class ProjectAdmin(ModelAdmin):
    list_display = (
        "name",
        "organization",
    )
    filter_horizontal = ("methods",)
    autocomplete_fields = ["region1", "city"]
    search_fields = ["name", "organization"]

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
