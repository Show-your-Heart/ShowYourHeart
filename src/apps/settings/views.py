from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.methods.models import Survey
from apps.settings.models import Network
from apps.users.services import send_network_assigned_mail


def admin_assigned_view(request, id):
    network = Network.objects.get(pk=id)
    send_network_assigned_mail(network)
    messages.success(
        request,
        _(
            "An email has been sent to the user to inform that he is now "
            " administrator of the network."
        ),
    )
    return HttpResponseRedirect(
        reverse_lazy("admin:settings_network_change", args=(network.id,))
    )


class WhatIsSocialBalanceView(TemplateView):
    template_name = "info/what_is_social_balance.html"


class GoodPracticesView(TemplateView):
    template_name = "info/good_practices.html"


class DocumentsView(TemplateView):
    template_name = "info/documents.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.request.user.profile.organization
        context["surveys"] = Survey.objects.filter(
            organization=context["organization"]
        )
        return context


class ResourcesView(TemplateView):
    template_name = "info/resources.html"


class ContactView(TemplateView):
    template_name = "info/contact.html"
