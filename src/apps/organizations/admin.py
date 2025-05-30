from django.contrib import admin

from project.admin import ModelAdmin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    list_display = (
        "name",
        "status",
    )
    common_fieldsets = [
        (
            ("Log"),
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    ]

    def get_fieldsets(self, request, obj=None):
        # Do not display "log fields" twice, display them only on a "Log" section
        log_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]
        default_fields = super().get_fieldsets(request, obj)

        filtered_default_fields = [
            (
                None,
                {
                    "fields": [
                        f for f in default_fields[0][1]["fields"] if f not in log_fields
                    ]
                },
            )
        ]
        return filtered_default_fields + self.common_fieldsets
