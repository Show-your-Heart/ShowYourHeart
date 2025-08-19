from django.contrib import admin
from django.urls import reverse
from django.utils.html import escapejs, format_html
from django.utils.translation import gettext as _
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin

from .forms import InvitationInlineForm, MethodForm
from .models import (
    Campaign,
    ExternalSurveyInvitation,
    Indicator,
    IndicatorResult,
    Invitation,
    List,
    ListItem,
    Method,
    Survey,
    Topic,
)


class TopicAdmin(ModelAdmin, TranslationAdmin):
    search_fields = ["name"]

    list_display = (
        "name",
        "description",
        "parent",
    )

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "description_en", "parent"],
            translatable_fields=["name", "description"],
            display_log=False,
        )


class IndicatorAdmin(ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["topics", "list_options"]

    list_display = (
        "project_id",
        "version",
        "name",
        "description",
        "is_direct_indicator",
    )
    conditional_fields = {
        "category": "is_direct_indicator == true",
        "condition": "is_direct_indicator == true",
        "formula": "is_direct_indicator == false",
    }

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "project_id",
                "version",
                "name_en",
                "description_en",
                "is_direct_indicator",
                "topics",
                "category",
                "data_type",
                "unit",
                "list_options",
                "condition",
                "formula",
                "validation",
                "message",
            ],
            translatable_fields=["name", "description"],
            display_log=False,
        )


class MethodAdmin(ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["sectors", "legal_structures", "network_owner"]
    search_fields = ["name"]
    filter_horizontal = ("indicators",)
    form = MethodForm

    list_display = (
        "name",
        "description",
        "network_owner",
        "unit_of_analysis",
        "active",
    )

    conditional_fields = {
        "external_surveys": f"unit_of_analysis != '{Method.UnitAnalysis.EXTERNAL_SURVEY}'",  # noqa: E501
    }

    def get_form(self, request, obj=None, **kwargs):
        # Add network_owner property to use it on formfield_for_manytomany
        if obj:
            self.network_owner = obj.network_owner
        return super().get_form(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # External surveys field must only display
        # methods for the same network and set as external survey
        if (db_field.name == "external_surveys") & hasattr(self, "network_owner"):
            kwargs["queryset"] = Method.objects.filter(
                network_owner=self.network_owner,
                unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY,
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "name_en",
                "description_en",
                "active",
                "network_owner",
                "unit_of_analysis",
                "indicators",
                "legal_structures",
                "sectors",
                "documentation",
                "external_surveys",
            ],
            translatable_fields=["name", "description"],
        )


admin.site.register(Method, MethodAdmin)


class ListAdmin(ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["items"]
    search_fields = ["title"]

    list_display = ("title",)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "enable_others", "items"],
            translatable_fields=["title"],
        )


class ListItemAdmin(ModelAdmin, TranslationAdmin):
    search_fields = ["title"]

    list_display = (
        "title",
        "active",
    )

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "formula", "value", "active"],
            translatable_fields=["title"],
        )


class CampaignAdmin(ModelAdmin):
    list_display = (
        "year",
        "name",
        "status",
    )
    filter_horizontal = ("methods",)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "year",
                "name",
                "status",
                "previous_campaign",
                "start_date",
                "end_date",
                "methods",
            ],
            translatable_fields=[],
        )


class SurveyAdmin(ModelAdmin):
    list_display = ("method", "campaign", "user", "status")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class IndicatorResultAdmin(ModelAdmin):
    list_display = (
        "survey",
        "indicator",
    )
    ordering = ["survey"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class InvitationInline(admin.StackedInline):
    model = Invitation
    verbose_name_plural = "Invitations"
    fk_name = "external_survey_invitation"
    extra = 0
    fields = (
        "name",
        "email",
        "status",
        "token",
        "actions_field",
    )
    tab = True  # Display the profile information on a new tab
    hide_title = True
    form = InvitationInlineForm
    ordering_field = ("name",)
    readonly_fields = (
        "status",
        "token",
        "actions_field",
    )

    @admin.display(description=_("Actions"))
    def actions_field(self, obj):
        if not obj:
            return "-"
        confirmed_verification_msg = _("Are you sure you want to send the invitation?")
        confirmed_verification_url = reverse(
            "methods:send_invitation",
            args=[obj.id],
        )
        confirmed_verification_text = _("Send invitation")
        buttons = [
            get_url_with_alert_msg(
                self,
                confirmed_verification_msg,
                confirmed_verification_url,
                confirmed_verification_text,
            )
        ]
        return format_html("<br><br>".join(buttons))


class ExternalSurveyInvitationAdmin(ModelAdmin):
    list_display = (
        "name",
        "external_survey",
        "campaign",
    )
    inlines = (InvitationInline,)
    readonly_fields = ("actions_field",)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "name",
                "external_survey",
                "campaign",
            ],
            translatable_fields=[],
            display_actions=True,
        )

    @admin.display(description=_("Actions"))
    def actions_field(self, obj):
        if not obj:
            return "-"
        confirmed_verification_msg = _("Are you sure you want to send the invitations?")
        confirmed_verification_url = reverse(
            "methods:send_invitations",
            args=[obj.id],
        )
        confirmed_verification_text = _("Send invitations")
        buttons = [
            get_url_with_alert_msg(
                self,
                confirmed_verification_msg,
                confirmed_verification_url,
                confirmed_verification_text,
            )
        ]
        return format_html("<br><br>".join(buttons))


def get_url_with_alert_msg(self, alert_msg, url, text):
    return format_html(
        f'<a class="bg-primary-600 block border border-transparent font-medium px-3'
        ' py-2 rounded-md text-white" style="width: 50%; text-align: center;"'
        f"href=\"javascript:if(confirm('{escapejs(alert_msg)}')) "
        f"window.location.href = '{url}'\">{text}</a>"
    )


admin.site.register(Topic, TopicAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(List, ListAdmin)
admin.site.register(ListItem, ListItemAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(IndicatorResult, IndicatorResultAdmin)
admin.site.register(ExternalSurveyInvitation, ExternalSurveyInvitationAdmin)
