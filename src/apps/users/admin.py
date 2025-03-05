from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escapejs, format_html
from django.utils.translation import gettext as _
from unfold.admin import ModelAdmin

from apps.users.forms import UserModelInlineForm
from apps.users.models import User, UserProfile
from project.admin import ModelAdminMixin


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields except the password."""

    class Meta:
        model = User
        fields = ("email",)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.validated = timezone.now()
        if commit:
            user.save()
        return user


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    verbose_name_plural = "User Profile"
    fk_name = "user"
    extra = 0
    fields = ("telephone",)
    can_delete = False
    tab = True  # Display the profile information on a new tab
    hide_title = True
    form = UserModelInlineForm

    def get_readonly_fields(self, request, obj=None):
        # Don't allow editing until the User exists
        readonly_fields = list(self.readonly_fields)
        if not obj:
            readonly_fields.extend(
                [
                    "telephone",
                ]
            )
        return readonly_fields


@admin.register(User)
class UserAdmin(ModelAdminMixin, BaseUserAdmin, ModelAdmin):
    list_display = (
        "email",
        "full_name",
        "is_staff",
        "is_superuser",
        "email_verified",
    )
    list_filter = ("is_superuser",)
    search_fields = ("email", "name", "surnames")
    ordering = ("email",)
    fieldsets = (("Autentication", {"fields": ("email", "password")}),)
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            _("Authentication"),
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    # common_fieldsets is not a standard ModelAdmin attribute. We extend
    # get_fieldsets to avoid having to repeat info in fieldsets and add_fieldsets.
    common_fieldsets = (
        (
            _("Personal details"),
            {
                "fields": (
                    "name",
                    "surnames",
                )
            },
        ),
        (
            _("Permissions and authorizations"),
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "email_verified",
                    "actions_field",
                    "roles_explanation_field",
                    "groups",
                ),
            },
        ),
        (
            _("Log"),
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    superuser_fields = (
        "is_superuser",
        "email_verified",
    )
    readonly_fields = (
        "roles_explanation_field",
        "actions_field",
    )

    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj) + self.common_fieldsets

    @admin.display(description=_("User roles information"))
    def roles_explanation_field(self, obj):
        groups_string = "".join(
            f"<li>{group.get('name')}: {group.get('description')}</li>"
            f"<li>{group.get('name')}: {group.get('description')}</li>"
            for group in settings.GROUPS.values()
        )
        return format_html(f"<ul> <li>{groups_string}</li> </ul>")

    @admin.display(description=_("Actions"))
    def actions_field(self, obj):
        if not obj or obj.email_verified:
            return "-"
        confirmed_verification_msg = _(
            "Are you sure you want to send an email to the user to set the password?"
        )
        confirmed_verification_url = reverse(
            "registration:welcome_email",
            args=[obj.id],
        )
        confirmed_verification_text = _("Send email to the user to set the password")
        buttons = [
            self._get_url_with_alert_msg(
                confirmed_verification_msg,
                confirmed_verification_url,
                confirmed_verification_text,
            )
        ]
        return format_html("<br><br>".join(buttons))

    def _get_url_with_alert_msg(self, alert_msg, url, text):
        return format_html(
            f'<a class="bg-primary-600 block border border-transparent font-medium px-3'
            ' py-2 rounded-md text-white" style="width: 50%; text-align: center;"'
            f"href=\"javascript:if(confirm('{escapejs(alert_msg)}')) "
            f"window.location.href = '{url}'\">{text}</a>"
        )


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
