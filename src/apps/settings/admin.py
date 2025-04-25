from django.contrib import admin
from django.urls import reverse
from django.utils.html import escapejs, format_html
from django.utils.translation import gettext as _
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin

from .models import LegalStructure, Network


class LegalStructureAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name",)


admin.site.register(LegalStructure, LegalStructureAdmin)


@admin.register(Network)
class NetworkAdmin(ModelAdmin):
    list_display = ("name", "parent_network", "network_admin")
    fieldsets = (("", {"fields": ("name", "network_admin", "parent_network")}),)

    common_fieldsets = (
        (
            _("Actions"),
            {"fields": ("actions_field",)},
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

    readonly_fields = ("actions_field",)

    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj) + self.common_fieldsets

    @admin.display(description=_("Actions"))
    def actions_field(self, obj):
        if not obj or not obj.network_admin:
            return "-"
        confirmed_verification_msg = _(
            "Are you sure you want to send an email to the user to notify he has been "
            "added as network admin?"
        )
        confirmed_verification_url = reverse(
            "settings:admin_assigned",
            args=[obj.id],
        )
        confirmed_verification_text = _(
            "Send email to the user to notify he has been added as network admin"
        )
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
