import json

from adminsortable2.admin import SortableAdminBase, SortableStackedInline
from django.contrib import admin
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import escapejs, format_html
from django.utils.translation import gettext as _
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from modeltranslation.admin import TabbedTranslationAdmin, TranslationStackedInline
from unfold.contrib.forms.widgets import WysiwygWidget

from apps.geodata.models import Region1
from apps.methods.mixins import prepare_method_fill_context, save_indicator_results
from apps.settings.models import LegalStructure
from project.admin import ImportExportModelAdmin, ModelAdmin, gov_admin_site
from project.decorators import gov_admin_register, register_with_default_templates
from project.utils.mixins import NetworkFilterMixin

from .forms import (
    IndicatorForm,
    IndicatorsSetForm,
    InvitationInlineForm,
    MethodForm,
    SectionForm,
    SectionInlineForm,
)
from .helpers import (
    get_form_sections,
    get_survey_stats,
)
from .models import (
    Campaign,
    ExternalSurveyInvitation,
    Group,
    GroupItem,
    Indicator,
    IndicatorResult,
    IndicatorsSet,
    Invitation,
    List,
    ListItem,
    Method,
    Section,
    Survey,
    Topic,
)
from .services import send_survey_status_update_email
from .views import BalanceReviewView


class TopicResource(resources.ModelResource):
    class Meta:
        model = Topic


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Topic)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Topic)
class TopicAdmin(ImportExportModelAdmin, TabbedTranslationAdmin):
    search_fields = ["name"]
    autocomplete_fields = ["parent"]

    list_display = (
        "name",
        "description",
        "parent",
    )

    resource_classes = [TopicResource]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "description_en", "parent"],
            translatable_fields=["name", "description"],
            display_log=False,
        )


class IndicatorResource(resources.ModelResource):
    topic_names = fields.Field(
        column_name="topic_names",
        attribute="topics",
        widget=ManyToManyWidget(Topic, field="name", separator="|"),
    )

    list_title = fields.Field(
        column_name="list_title",
        attribute="list_options",
        widget=ForeignKeyWidget(List, field="title"),
    )

    group_title = fields.Field(
        column_name="group_title",
        attribute="group",
        widget=ForeignKeyWidget(Group, field="title"),
    )

    group_2_title = fields.Field(
        column_name="group_2_title",
        attribute="group_2",
        widget=ForeignKeyWidget(Group, field="title"),
    )

    class Meta:
        model = Indicator


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Indicator)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Indicator)
class IndicatorAdmin(
    NetworkFilterMixin, ImportExportModelAdmin, TabbedTranslationAdmin
):
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
    numeric_types_js = json.dumps(Indicator.numeric_types)

    conditional_fields = {
        "category": "is_direct_indicator == true",
        "display_indirect": "is_direct_indicator == false",
        "condition": """
                is_direct_indicator == true ||
                (is_direct_indicator == false && display_indirect == true)
            """,
        "formula": "is_direct_indicator == false",
        "list_options": f"{list_types_js}.includes(data_type)",
        "group": f"{group_types_js}.includes(data_type) && is_group_indicator == true",
        "group_total": f"""{numeric_types_js}.includes(data_type)
                        && is_group_indicator == true""",
        "group_2": f"""{group_types_js}.includes(data_type)
                        && is_group_indicator == true""",
        "group_2_total": f"""{numeric_types_js}.includes(data_type)
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
                "display_indirect",
                "is_group_indicator",
                "mandatory",
                "topics",
                "category",
                "data_type",
                "unit",
                "list_options",
                "group",
                "group_total",
                "group_2",
                "group_2_total",
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


class IndicatorsSetResource(resources.ModelResource):
    indicators_code = fields.Field(
        column_name="indicators_code",
        attribute="indicators",
        widget=ManyToManyWidget(Indicator, field="code", separator="|"),
    )

    class Meta:
        model = IndicatorsSet


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=IndicatorsSet)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=IndicatorsSet)
class IndicatorsSetAdmin(
    NetworkFilterMixin, ImportExportModelAdmin, TabbedTranslationAdmin
):
    autocomplete_fields = []
    form = IndicatorsSetForm
    search_fields = ["code", "name"]

    list_display = (
        "code",
        "version",
        "name",
        "description",
    )

    resource_classes = [IndicatorsSetResource]


class SectionResource(resources.ModelResource):
    indicators_code = fields.Field(
        column_name="indicators_code",
        attribute="indicators",
        widget=ManyToManyWidget(Indicator, field="code", separator="|"),
    )
    indicators_sets_code = fields.Field(
        column_name="indicators_sets_code",
        attribute="indicators_sets",
        widget=ManyToManyWidget(IndicatorsSet, field="code", separator="|"),
    )

    class Meta:
        model = Section


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Section)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Section)
class SectionAdmin(
    ImportExportModelAdmin,
    TabbedTranslationAdmin,
):
    search_fields = ["title"]
    form = SectionForm

    list_display = (
        "title",
        "description",
        "parent",
        "method",
        "order",
    )

    resource_classes = [SectionResource]


class SectionInline(TranslationStackedInline, SortableStackedInline):
    model = Section
    extra = 0
    tab = True  # Display the profile information on a new tab
    hide_title = True
    form = SectionInlineForm
    ordering_field = "order"
    hide_ordering_field = True
    collapsible = True
    template = "admin/methods/section/stacked_inline.html"


class MethodResource(resources.ModelResource):
    indicators_code = fields.Field(
        column_name="indicators_code",
        attribute="indicators",
        widget=ManyToManyWidget(Indicator, field="code", separator="|"),
    )

    indicators_sets_code = fields.Field(
        column_name="indicators_sets_code",
        attribute="indicators_sets",
        widget=ManyToManyWidget(IndicatorsSet, field="code", separator="|"),
    )

    region1s_name = fields.Field(
        column_name="region1s_name",
        attribute="region1",
        widget=ManyToManyWidget(Region1, field="name", separator="|"),
    )

    legal_structures_name = fields.Field(
        column_name="legal_structures_name",
        attribute="legal_structures",
        widget=ManyToManyWidget(LegalStructure, field="name", separator="|"),
    )

    class Meta:
        model = Method


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Method)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Method)
class MethodAdmin(
    NetworkFilterMixin,
    SortableAdminBase,
    ImportExportModelAdmin,
    TabbedTranslationAdmin,
):
    autocomplete_fields = ["sectors", "legal_structures", "networks", "region1"]
    search_fields = ["name"]
    filter_horizontal = ("indicators", "indicators_sets", "external_surveys")
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
        "external_survey_category": f"unit_of_analysis == '{Method.UnitAnalysis.EXTERNAL_SURVEY}'",  # noqa: E501
    }

    change_form_template = "admin/methods/method/change_form.html"

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }

    resource_classes = [MethodResource]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "external_surveys":
            kwargs["queryset"] = Method.objects.filter(
                unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY,
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "name_en",
                "description_en",
                "version",
                "unit_of_analysis",
                "external_survey_category",
                "indicators",
                "indicators_sets",
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


class GroupResource(resources.ModelResource):
    class Meta:
        model = Group


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Group)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Group)
class GroupAdmin(ImportExportModelAdmin, TabbedTranslationAdmin):
    search_fields = ["title"]

    list_display = ("title",)

    resource_classes = [GroupResource]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "items"],
            # main_fields=["title_en", "enable_others", "items"],
            translatable_fields=["title"],
        )


class GroupItemResource(resources.ModelResource):
    group_titles = fields.Field(
        column_name="group_titles",
        attribute="groups",
        widget=ManyToManyWidget(Group, field="title", separator="|"),
    )

    class Meta:
        model = GroupItem


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=GroupItem)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=GroupItem)
class GroupItemAdmin(ImportExportModelAdmin, TabbedTranslationAdmin):
    search_fields = ["title", "suffix"]

    list_display = ("title",)

    resource_classes = [GroupItemResource]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "suffix"],
            translatable_fields=["title"],
        )


class ListResource(resources.ModelResource):
    class Meta:
        model = List


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=List)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=List)
class ListAdmin(ImportExportModelAdmin, TabbedTranslationAdmin):
    search_fields = ["title"]

    list_display = ("title",)

    resource_classes = [ListResource]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "enable_others", "items"],
            translatable_fields=["title"],
        )


class ListItemResource(resources.ModelResource):
    list_titles = fields.Field(
        column_name="list_titles",
        attribute="lists",
        widget=ManyToManyWidget(List, field="title", separator="|"),
    )

    class Meta:
        model = ListItem


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=ListItem)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=ListItem)
class ListItemAdmin(ImportExportModelAdmin, TabbedTranslationAdmin):
    search_fields = ["title"]

    list_display = ("title",)

    resource_classes = [ListItemResource]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "formula", "value"],
            translatable_fields=["title"],
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Campaign)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Campaign)
class CampaignAdmin(NetworkFilterMixin, ModelAdmin, TabbedTranslationAdmin):
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
            method_fill_context = prepare_method_fill_context(
                pk, None, None, None, None, request
            )
            survey = get_object_or_404(Survey, pk=pk)
            method_fill_context.update(
                {
                    "survey_id": survey.id,
                    "validate_survey": True
                    if request.GET.get("action") == "info"
                    else False,
                }
            )

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
                    method_fill_context,
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
                    "HX-Trigger": '{ "hide-modal": { "id": "edit-survey-modal" }, '
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

        email_log = None
        notification_type = "success"
        try:
            result = send_survey_status_update_email(request, pk, survey.status)
            if result:
                email_log = _("An email to the contact has been sent.") + f"[{result}]"
        except Exception as error:
            email_log = str(error)
            notification_type = "error"

        survey.method.sections = get_form_sections(survey.method)
        stats = get_survey_stats(survey, survey.method, survey.campaign)
        survey.totalProgress = stats["totalProgress"]

        status = []
        for s in Survey.Status:
            status.append({"id": s.value, "name": s.label})

        msg = _("Balance status successfuly updated.")
        if email_log:
            msg = "".join([msg, email_log])

        return HttpResponse(
            render(
                request,
                "components/methods/survey_review_row.html",
                {"survey": survey, "status": status},
            ),
            headers={
                "HX-Trigger": "{ "
                + '"notification": { "type": "'
                + notification_type
                + '", "text": "'
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
        "updated_at",
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
        "send_date",
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
    list_display = ("name", "external_survey", "organization")
    inlines = (InvitationInline,)
    readonly_fields = ("actions_field",)
    autocomplete_fields = ["campaign", "external_survey"]
    search_fields = ["name", "external_survey__name", "organization__name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "name",
                "external_survey",
                "campaign",
                "organization",
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
