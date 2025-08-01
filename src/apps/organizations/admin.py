from django.contrib import admin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from project.admin import ModelAdmin

from .forms import OrganizationAdminForm
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    form = OrganizationAdminForm
    list_display = (
        "name",
        "status",
    )
    filter_horizontal = ("methods",)

    list_filter = [("status", ChoicesDropdownFilter)]

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

        if self.is_legal_structure_readonly(obj):
            # When the field is set as readonly is placed at the bottom of the list
            # Replace it on his original place
            fieldsets[0][1]["fields"].remove("legal_structure")
            fieldsets[0][1]["fields"].insert(
                len(fieldsets[0][1]["fields"]) - 1, "legal_structure"
            )

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
