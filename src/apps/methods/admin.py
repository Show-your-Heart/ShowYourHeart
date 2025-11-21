import json

from adminsortable2.admin import SortableAdminBase, SortableStackedInline
from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import escapejs, format_html
from django.utils.translation import gettext as _
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin, gov_admin_site
from project.decorators import gov_admin_register, register_with_default_templates

from .forms import IndicatorForm, InvitationInlineForm, MethodForm, SectionInlineForm
from .models import (
    Campaign,
    ExternalSurveyInvitation,
    Indicator,
    IndicatorResult,
    Invitation,
    List,
    ListItem,
    Method,
    Section,
    Survey,
    Topic,
)
from .views import BalanceReview


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Topic)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Topic)
class TopicAdmin(ModelAdmin, TranslationAdmin):
    search_fields = ["name"]
    autocomplete_fields = ["parent"]

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


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Indicator)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Indicator)
class IndicatorAdmin(ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["topics", "list_options"]
    form = IndicatorForm
    search_fields = ["code", "name"]

    list_display = (
        "code",
        "version",
        "name",
        "description",
        "is_direct_indicator",
    )

    list_types_js = json.dumps(Indicator.list_types)

    conditional_fields = {
        "category": "is_direct_indicator == true",
        "condition": "is_direct_indicator == true",
        "formula": "is_direct_indicator == false",
        "list_options": f"{list_types_js}.includes(data_type)",
    }

    exclude = ("dependant_indicators",)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "code",
                "version",
                "name_en",
                "description_en",
                "is_direct_indicator",
                "mandatory",
                "topics",
                "category",
                "data_type",
                "unit",
                "list_options",
                "condition",
                "formula",
                "validation",
                "message_en",
            ],
            translatable_fields=["name", "description", "message"],
            display_log=False,
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            default_value = Indicator._meta.get_field("is_direct_indicator").default
            form.base_fields["is_direct_indicator"].initial = default_value
        return form


class SectionInline(SortableStackedInline, admin.StackedInline):
    model = Section
    extra = 0
    fields = (
        "title",
        "parent",
        "method",
        "indicators",
    )
    tab = True  # Display the profile information on a new tab
    hide_title = True
    form = SectionInlineForm
    ordering_field = "order"
    hide_ordering_field = True
    collapsible = True
    template = "admin/methods/section/stacked_inline.html"


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Method)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Method)
class MethodAdmin(SortableAdminBase, ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["sectors", "legal_structures", "network_owner"]
    search_fields = ["name"]
    filter_horizontal = ("indicators",)
    form = MethodForm
    inlines = (SectionInline,)

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
        if db_field.name == "external_surveys":
            if hasattr(self, "network_owner"):
                kwargs["queryset"] = Method.objects.filter(
                    network_owner=self.network_owner,
                    unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY,
                )
            else:
                kwargs["queryset"] = Method.objects.none()
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


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=List)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=List)
class ListAdmin(ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["items"]
    search_fields = ["title"]

    list_display = ("title",)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "enable_others", "items"],
            translatable_fields=["title"],
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=ListItem)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=ListItem)
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


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Campaign)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Campaign)
class CampaignAdmin(ModelAdmin):
    list_display = (
        "year",
        "name",
        "status",
    )
    filter_horizontal = ("methods",)
    search_fields = ["name"]
    autocomplete_fields = ["previous_campaign"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "year",
                "name_en",
                "status",
                "previous_campaign",
                "start_date",
                "end_date",
                "methods",
            ],
            translatable_fields=["name"],
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Survey)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Survey)
class SurveyAdmin(ModelAdmin):
    list_display = ("method", "campaign", "user", "status")
    search_fields = ["method__name", "method__network_owner__name"]

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_urls(self):
        urls = super().get_urls() + [
            path(
                "review-balances",
                self.admin_site.admin_view(BalanceReview.as_view(model_admin=self)),
                name="review_balances",
            ),
        ]
        return urls


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=IndicatorResult)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=IndicatorResult)
class IndicatorResultAdmin(ModelAdmin):
    list_display = (
        "survey",
        "indicator",
    )
    ordering = ["survey"]
    search_fields = ["survey__method__name"]

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


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
    ordering_field = "name"
    readonly_fields = (
        "status",
        "token",
        "actions_field",
    )
    collapsible = True

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


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=ExternalSurveyInvitation)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=ExternalSurveyInvitation)
class ExternalSurveyInvitationAdmin(ModelAdmin):
    list_display = (
        "name",
        "external_survey",
        "campaign",
    )
    inlines = (InvitationInline,)
    readonly_fields = ("actions_field",)
    autocomplete_fields = ["campaign", "external_survey"]
    search_fields = ["name"]

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
