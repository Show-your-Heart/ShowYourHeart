from django.contrib import admin

from project.admin import ModelAdmin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    list_display = (
        "name",
        "status",
    )
