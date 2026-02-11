import json

from adminsortable2.admin import SortableAdminBase, SortableStackedInline
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import escapejs, format_html
from django.utils.translation import gettext as _
from import_export import resources
from modeltranslation.admin import TranslationAdmin

from apps.methods.mixins import save_indicator_results
from project.admin import ImportExportModelAdmin, ModelAdmin, gov_admin_site
from project.decorators import gov_admin_register, register_with_default_templates
from project.mixins import NetworkFilterMixin

from .forms import (
    IndicatorForm,
    InvitationInlineForm,
    MethodForm,
    SectionInlineForm,
    get_dynamic_form,
)
from .helpers import (
    get_form_sections,
    get_survey_stats,
)
from .mixins import (
    get_initial_values,
    get_previous_campaign_answers,
    get_sections,
    get_sections_data,
)
from .models import (
    Campaign,
    ExternalSurveyInvitation,
    Group,
    GroupItem,
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
from .views import BalanceReviewView


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


class IndicatorResource(resources.ModelResource):
    class Meta:
        model = Indicator


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Indicator)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Indicator)
class IndicatorAdmin(NetworkFilterMixin, ImportExportModelAdmin, TranslationAdmin):
    autocomplete_fields = ["topics", "list_options"]
    form = IndicatorForm
    search_fields = ["code", "name"]

    list_display = (
        "code",
        "version",
        "name",
        "description",
        "is_direct_indicator",
        "is_group_indicator",
    )

    list_types_js = json.dumps(Indicator.list_types)
    group_types_js = json.dumps(Indicator.group_types)

    conditional_fields = {
        "category": "is_direct_indicator == true",
        "condition": "is_direct_indicator == true",
        "formula": "is_direct_indicator == false",
        "list_options": f"{list_types_js}.includes(data_type)",
        "group": f"{group_types_js}.includes(data_type) && is_group_indicator == true",
        "group_2": f"""{group_types_js}.includes(data_type)
                        && is_group_indicator == true""",
    }

    exclude = ("dependant_indicators",)

    resource_classes = [IndicatorResource]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "code",
                "version",
                "name_en",
                "description_en",
                "is_direct_indicator",
                "is_group_indicator",
                "mandatory",
                "topics",
                "category",
                "data_type",
                "unit",
                "list_options",
                "group",
                "group_2",
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
class MethodAdmin(NetworkFilterMixin, SortableAdminBase, ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["sectors", "legal_structures", "networks", "region1"]
    search_fields = ["name"]
    filter_horizontal = ("indicators",)
    form = MethodForm
    inlines = (SectionInline,)

    list_display = (
        "name",
        "description",
        "unit_of_analysis",
        "version",
    )

    conditional_fields = {
        "external_surveys": f"unit_of_analysis != '{Method.UnitAnalysis.EXTERNAL_SURVEY}'",  # noqa: E501
    }

    change_form_template = "admin/methods/method/change_form.html"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # External surveys field must only display
        # methods for the same network and set as external survey
        if db_field.name == "external_surveys":
            if hasattr(self, "networks"):
                kwargs["queryset"] = Method.objects.filter(
                    networks=self.networks,
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
                "version",
                "unit_of_analysis",
                "indicators",
                "legal_structures",
                "sectors",
                "region1",
                "documentation",
                "external_surveys",
            ],
            translatable_fields=["name", "description"],
        )

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        method = self.get_object(request, object_id)
        campaign = None
        if method is not None:
            campaign = method.campaign_methods.order_by("created_at").last()
        extra_context["campaign_id"] = campaign.id if campaign else None

        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Group)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Group)
class GroupAdmin(ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["items"]
    search_fields = ["title"]

    list_display = ("title",)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "items"],
            # main_fields=["title_en", "enable_others", "items"],
            translatable_fields=["title"],
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=GroupItem)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=GroupItem)
class GroupItemAdmin(ModelAdmin, TranslationAdmin):
    search_fields = ["title", "suffix"]

    list_display = ("title",)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "suffix"],
            translatable_fields=["title"],
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

    list_display = ("title",)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "formula", "value"],
            translatable_fields=["title"],
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Campaign)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Campaign)
class CampaignAdmin(NetworkFilterMixin, ModelAdmin):
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
    search_fields = ["method__name"]

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_urls(self):
        urls = [
            path(
                "review-balances",
                self.admin_site.admin_view(BalanceReviewView.as_view(model_admin=self)),
                name="review_balances",
            ),
            path(
                "review_survey_actions/<uuid:pk>/",
                self.admin_site.admin_view(
                    self.review_survey_action,
                ),
                name="review_survey_actions",
            ),
            path(
                "survey_status_change/<uuid:pk>",
                self.admin_site.admin_view(
                    self.survey_status_update,
                ),
                name="survey_status_change",
            ),
        ] + super().get_urls()
        return urls

    # @method_decorator(require_GET)
    def review_survey_action(self, request, pk, **kwargs):
        if request.method == "GET":
            survey = get_object_or_404(Survey, pk=pk)

            placeholder_dict = get_previous_campaign_answers(
                survey.campaign.id, survey.method.id, survey.user
            )

            readonly = False
            # Get the current survey already started
            try:
                form = get_dynamic_form(
                    survey.method,
                    IndicatorResult.objects.filter(survey=survey),
                    readonly,
                    placeholder_dict,
                )

            except ObjectDoesNotExist:
                # If there is none, get new survey
                form = get_dynamic_form(survey.method, [], False, placeholder_dict)

            sections = get_sections(survey.method, form(data=request.POST or None))

            try:
                indicators = list(
                    Method.objects.get(id=survey.method.id).indicators.all().values()
                )
                for i in indicators:
                    i["unit"] = Indicator.Unit(i["unit"]).label if i["unit"] else ""

            except Method.DoesNotExist:
                indicators = list([])

            if request.GET.get("action") == "edit":
                # Display edit modal event
                headers = {
                    "HX-Trigger": '{ "show-modal": { "id": "edit-survey-modal", '
                    + '"titleDetails": " - '
                    + survey.organization.vat_number
                    + " "
                    + survey.organization.name
                    + '" } }',
                }

            elif request.GET.get("action") == "info":
                headers = {}

            return HttpResponse(
                render(
                    request,
                    "admin/methods/method_fill.html",
                    {
                        "method_name": survey.method.name,
                        "initial_values": get_initial_values(survey),
                        "readonly": readonly,
                        "form": form,
                        "sections": sections,
                        "sections_data": get_sections_data(sections),
                        "indicators": indicators,
                        "survey_id": survey.id,
                        "validate_survey": True
                        if request.GET.get("action") == "info"
                        else False,
                    },
                ),
                headers=headers,
            )

        elif request.method == "POST":
            action = request.POST.get("action")

            survey = Survey.objects.get(id=pk)

            current_date = timezone.now()

            if action == "submit":
                survey.status = Survey.Status.CLOSED
                survey.closed_date = current_date

            survey.modified_date = current_date

            survey.save()

            save_indicator_results(survey.method.id, request, survey)

            msg = _("Balance successfuly updated.")

            return HttpResponse(
                "",
                headers={
                    "HX-Trigger": '{ "hide-modal": {}, '
                    + '"notification": { "type": "success", "text": "'
                    + msg
                    + '" } }',
                },
            )

    def survey_status_update(self, request, pk, **kwargs):
        survey = get_object_or_404(Survey, pk=pk)
        survey.status = int(request.POST.get("status-selection"))

        current_date = timezone.now()
        if survey.status == Survey.Status.CLOSED:
            survey.closed_date = current_date
        elif survey.status == Survey.Status.TECH_VALIDATED:
            survey.validated_date = current_date
        elif survey.status == Survey.Status.QUALITY_CHECKED:
            survey.evaluated_date = current_date

        survey.save()

        survey.method.sections = get_form_sections(survey.method)
        stats = get_survey_stats(survey, survey.method, survey.campaign)
        survey.totalProgress = stats["totalProgress"]

        status = []
        for s in Survey.Status:
            status.append({"id": s.value, "name": s.label})

        msg = _("Balance status successfuly updated.")
        return HttpResponse(
            render(
                request,
                "components/methods/survey_review_row.html",
                {"survey": survey, "status": status},
            ),
            headers={
                "HX-Trigger": "{ "
                + '"notification": { "type": "success", "text": "'
                + msg
                + '" } }',
            },
        )


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
