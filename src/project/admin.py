from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from post_office.admin import EmailTemplateAdmin
from post_office.models import EmailTemplate
from unfold.admin import ModelAdmin as BaseModelAdmin
from unfold.sites import UnfoldAdminSite

from apps.organizations.models import Organization
from project.decorators import gov_admin_register

from .helpers import available_apps_to_dict


class ModelAdminMixin(object):
    base_readonly_fields = ("created_at", "created_by", "updated_at")
    # superuser_fields will be read-only unless you are superuser
    superuser_fields = ()

    def get_superuser_fields(self):
        return self.superuser_fields

    def get_base_readonly_fields(self):
        return self.base_readonly_fields

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        fields = tuple(set(fields + self.get_base_readonly_fields()))
        if not request.user.is_superuser:
            return tuple(set(fields + self.get_superuser_fields()))
        return fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        This method ensures that any Inline that is included will fill
        the field `created_by` automatically.

        The interesting fields to play with are:
        for form in formset:
            print("Instance str representation:", form.instance)
            print("Instance dict:", form.instance.__dict__)
            print("Initial for ID field:", form["id"].initial)
            print("Has changed:", form.has_changed())

        form["id"].initial will be None if it's a new entry.
        """
        for form in formset:
            model = type(form.instance)
            if not form["id"].initial and hasattr(model, "created_by"):
                # created_by will not appear in the form dictionary because
                # is read_only, but we can anyway set it directly at the yet-
                # to-be-saved instance.
                form.instance.created_by = request.user
        super().save_formset(request, form, formset, change)


class ModelAdmin(ModelAdminMixin, BaseModelAdmin):
    list_filter_submit = True

    @staticmethod
    def build_fieldsets(
        main_fields, translatable_fields=None, display_log=True, display_actions=False
    ):
        fields = [
            (_("Add/Edit"), {"fields": main_fields, "classes": ("tab",)}),
        ]

        if translatable_fields:
            other_langs = [lang[0] for lang in settings.LANGUAGES if lang[0] != "en"]
            translation_fields = [
                f"{field}_{lang}"
                for field in translatable_fields
                for lang in other_langs
            ]
            fields.append(
                (
                    _("Translations"),
                    {"fields": translation_fields, "classes": ("tab",)},
                ),
            )

        if display_actions:
            fields.append(
                (
                    _("Actions"),
                    {"fields": ("actions_field",)},
                ),
            )

        if display_log:
            fields.append(
                (
                    ("Log"),
                    {
                        "fields": (
                            "created_by",
                            "created_at",
                            "updated_at",
                        ),
                        "classes": ("tab",),
                    },
                )
            )

        return fields


action_names = {
    ADDITION: pgettext_lazy("logentry_admin:action_type", "Addition"),
    DELETION: pgettext_lazy("logentry_admin:action_type", "Deletion"),
    CHANGE: pgettext_lazy("logentry_admin:action_type", "Change"),
}


class ActionListFilter(admin.SimpleListFilter):
    title = _("action")
    parameter_name = "action_flag"

    def lookups(self, request, model_admin):
        return action_names.items()

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(action_flag=self.value())
        return queryset


class UserListFilter(admin.SimpleListFilter):
    title = _("staff user")
    parameter_name = "user"

    def lookups(self, request, model_admin):
        staff = get_user_model().objects.filter(is_staff=True)
        return ((s.id, force_str(s)) for s in staff)

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(user_id=self.value(), user__is_staff=True)
        return queryset


@admin.register(LogEntry)
class LogEntryAdmin(BaseModelAdmin):
    date_hierarchy = "action_time"

    readonly_fields = [f.name for f in LogEntry._meta.fields] + [
        "object_link",
        "action_description",
        "user_link",
        "get_change_message",
    ]

    fieldsets = (
        (
            _("Metadata"),
            {
                "fields": (
                    "action_time",
                    "user_link",
                    "action_description",
                    "object_link",
                )
            },
        ),
        (
            _("Details"),
            {
                "fields": (
                    "get_change_message",
                    "content_type",
                    "object_id",
                    "object_repr",
                )
            },
        ),
    )

    list_filter = [UserListFilter, "content_type", ActionListFilter]

    search_fields = ["object_repr", "change_message"]

    list_display_links = [
        "action_time",
        "get_change_message",
    ]
    list_display = [
        "action_time",
        "user_link",
        "content_type",
        "object_link",
        "action_description",
        "get_change_message",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return (
            request.user.is_superuser or request.user.has_perm("admin.change_logentry")
        ) and request.method != "POST"

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        object_link = escape(obj.object_repr)
        content_type = obj.content_type

        if obj.action_flag != DELETION and content_type is not None:
            # try returning an actual link instead of object repr string
            try:
                url = reverse(
                    "admin:{}_{}_change".format(
                        content_type.app_label, content_type.model
                    ),
                    args=[obj.object_id],
                )
                object_link = '<a href="{}">{}</a>'.format(url, object_link)
            except NoReverseMatch:
                pass
        return mark_safe(object_link)

    object_link.admin_order_field = "object_repr"
    object_link.short_description = _("object")

    def user_link(self, obj):
        content_type = ContentType.objects.get_for_model(type(obj.user))
        user_link = escape(force_str(obj.user))
        try:
            # try returning an actual link instead of object repr string
            url = reverse(
                "admin:{}_{}_change".format(content_type.app_label, content_type.model),
                args=[obj.user.pk],
            )
            user_link = '<a href="{}">{}</a>'.format(url, user_link)
        except NoReverseMatch:
            pass
        return mark_safe(user_link)

    user_link.admin_order_field = "user"
    user_link.short_description = _("user")

    def get_queryset(self, request):
        queryset = super(LogEntryAdmin, self).get_queryset(request)
        return queryset.prefetch_related("content_type")

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def action_description(self, obj):
        return action_names[obj.action_flag]

    action_description.short_description = _("action")

    def get_change_message(self, obj):
        # TODO: is this still required in newer Django versions?
        return obj.change_message

    get_change_message.short_description = _("change message")


# Create a custom admin site for non-superuser admins like gov admin
class GovAdminSite(UnfoldAdminSite):
    index_template = "admin/syh_index.html"
    app_index_template = "admin/syh_app_index_template.html"

    def is_app_active(self, app, request):
        return True if app["app_url"] in request.path else False

    def is_model_active(self, model, request):
        return True if model["admin_url"] in request.path else False

    def each_context(self, request):
        context = super().each_context(request)

        apps_dict = available_apps_to_dict(context["available_apps"])
        request_path = request.get_full_path()
        request_path_array = request_path.split("?")[0].split("/")
        relative_path = request_path_array[len(request_path_array) - 1]

        main_menu = []
        if apps_dict:
            main_menu = [
                {
                    "app_name": "organizations",
                    "name": _("Entities"),
                    "icon": "group",
                    "url": apps_dict["Organizations"]["app_url"],
                    "is_active": self.is_app_active(apps_dict["Organizations"], request)
                    and (
                        relative_path
                        not in ["registration-requests", "review-balances"]
                    ),
                    "app": apps_dict["Organizations"],
                    "items": [
                        {
                            "name": _(
                                apps_dict["Organizations"]["models_dict"][
                                    "Organization"
                                ]["name"]
                            ),
                            "url": apps_dict["Organizations"]["models_dict"][
                                "Organization"
                            ]["admin_url"],
                            "is_active": self.is_model_active(
                                apps_dict["Organizations"]["models_dict"][
                                    "Organization"
                                ],
                                request,
                            ),
                        },
                        {
                            "name": _(
                                apps_dict["Organizations"]["models_dict"]["Project"][
                                    "name"
                                ]
                            ),
                            "url": apps_dict["Organizations"]["models_dict"]["Project"][
                                "admin_url"
                            ],
                            "is_active": self.is_model_active(
                                apps_dict["Organizations"]["models_dict"]["Project"],
                                request,
                            ),
                        },
                    ],
                },
                {
                    "app_name": "methods",
                    "name": _("Methods management"),
                    "icon": "adjustments-horizontal",
                    "url": apps_dict["Methods"]["app_url"],
                    "is_active": self.is_app_active(apps_dict["Methods"], request)
                    and (
                        relative_path
                        not in ["registration-requests", "review-balances"]
                    ),
                    "app": apps_dict["Methods"],
                    "items": [
                        {
                            "name": apps_dict["Methods"]["models_dict"]["Campaign"][
                                "name"
                            ],
                            "url": apps_dict["Methods"]["models_dict"]["Campaign"][
                                "admin_url"
                            ],
                            "is_active": self.is_model_active(
                                apps_dict["Methods"]["models_dict"]["Campaign"], request
                            ),
                        },
                        {
                            "name": apps_dict["Methods"]["models_dict"]["Method"][
                                "name"
                            ],
                            "url": apps_dict["Methods"]["models_dict"]["Method"][
                                "admin_url"
                            ],
                            "is_active": self.is_model_active(
                                apps_dict["Methods"]["models_dict"]["Method"], request
                            ),
                        },
                        {
                            "name": apps_dict["Methods"]["models_dict"][
                                "ExternalSurveyInvitation"
                            ]["name"],
                            "url": apps_dict["Methods"]["models_dict"][
                                "ExternalSurveyInvitation"
                            ]["admin_url"],
                            "is_active": self.is_model_active(
                                apps_dict["Methods"]["models_dict"][
                                    "ExternalSurveyInvitation"
                                ],
                                request,
                            ),
                        },
                        {
                            "name": apps_dict["Methods"]["models_dict"]["Indicator"][
                                "name"
                            ],
                            "url": apps_dict["Methods"]["models_dict"]["Indicator"][
                                "admin_url"
                            ],
                            "is_active": self.is_model_active(
                                apps_dict["Methods"]["models_dict"]["Indicator"],
                                request,
                            ),
                        },
                        {
                            "name": apps_dict["Methods"]["models_dict"]["List"]["name"],
                            "url": apps_dict["Methods"]["models_dict"]["List"][
                                "admin_url"
                            ],
                            "is_active": self.is_model_active(
                                apps_dict["Methods"]["models_dict"]["List"], request
                            ),
                        },
                        {
                            "name": apps_dict["Methods"]["models_dict"]["ListItem"][
                                "name"
                            ],
                            "url": apps_dict["Methods"]["models_dict"]["ListItem"][
                                "admin_url"
                            ],
                            "is_active": self.is_model_active(
                                apps_dict["Methods"]["models_dict"]["ListItem"],
                                request,
                            ),
                        },
                        {
                            "name": apps_dict["Methods"]["models_dict"]["Topic"][
                                "name"
                            ],
                            "url": apps_dict["Methods"]["models_dict"]["Topic"][
                                "admin_url"
                            ],
                            "is_active": self.is_model_active(
                                apps_dict["Methods"]["models_dict"]["Topic"], request
                            ),
                        },
                    ],
                },
                {
                    "name": "Features",
                    "icon": "clipboard-list",
                    "is_active": relative_path
                    in ["registration-requests", "review-balances"],
                    "items": [
                        {
                            "name": _("Registration Requests"),
                            "url": reverse_lazy("gov_admin:registration_requests"),
                            "is_active": ("registration-requests" in request_path),
                        },
                        {
                            "name": _("Review Balances"),
                            "url": reverse_lazy("gov_admin:review_balances"),
                            "is_active": ("review-balances" in request_path),
                        },
                        {"name": _("Documents")},
                    ],
                },
                {
                    "name": "Settings",
                    "icon": "cog",
                    "url": apps_dict["Settings"]["app_url"],
                    "is_active": self.is_app_active(apps_dict["Settings"], request)
                    or self.is_app_active(apps_dict["Users"], request)
                    or self.is_app_active(apps_dict["Geodata"], request)
                    or self.is_app_active(apps_dict["Post Office"], request),
                    "app": apps_dict["Settings"],
                    "items": [
                        {
                            "name": apps_dict["Post Office"]["models_dict"][
                                "EmailTemplate"
                            ]["name"],
                            "url": apps_dict["Post Office"]["models_dict"][
                                "EmailTemplate"
                            ]["admin_url"],
                            "is_active": self.is_model_active(
                                apps_dict["Post Office"]["models_dict"][
                                    "EmailTemplate"
                                ],
                                request,
                            ),
                        },
                        {
                            "name": apps_dict["Users"]["models_dict"]["User"]["name"],
                            "url": apps_dict["Users"]["models_dict"]["User"][
                                "admin_url"
                            ],
                            "is_active": self.is_model_active(
                                apps_dict["Users"]["models_dict"]["User"], request
                            ),
                        },
                        {
                            "name": _("Location data"),
                            "url": apps_dict["Geodata"]["app_url"],
                            "is_active": self.is_app_active(
                                apps_dict["Geodata"], request
                            ),
                        },
                        {
                            "name": apps_dict["Settings"]["models_dict"]["Network"][
                                "name"
                            ],
                            "url": apps_dict["Settings"]["models_dict"]["Network"][
                                "admin_url"
                            ],
                            "is_active": self.is_model_active(
                                apps_dict["Settings"]["models_dict"]["Network"],
                                request,
                            ),
                        },
                        {
                            "name": apps_dict["Settings"]["models_dict"][
                                "LegalStructure"
                            ]["name"],
                            "url": apps_dict["Settings"]["models_dict"][
                                "LegalStructure"
                            ]["admin_url"],
                            "is_active": self.is_model_active(
                                apps_dict["Settings"]["models_dict"]["LegalStructure"],
                                request,
                            ),
                        },
                    ],
                },
                {"name": "Auxiliary data", "icon": "book", "items": []},
            ]

        context.update(
            {
                "main_menu": main_menu,
            }
        )
        return context

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["pending_registrations_requests"] =  Organization.objects.filter(
            status=Organization.Status.PENDING
        ).count()
        return super(GovAdminSite, self).index(request, extra_context)

gov_admin_site = GovAdminSite(name="gov_admin")


@gov_admin_register(gov_admin_site, model=EmailTemplate)
class MyEmailTemplateAdmin(EmailTemplateAdmin):
    pass
