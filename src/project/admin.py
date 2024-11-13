from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from unfold.admin import ModelAdmin as BaseModelAdmin


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
    pass


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
