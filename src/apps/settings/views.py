from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.methods.models import Campaign, Survey
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
        organization = self.request.user.profile.organization
        context["organization"] = organization

        surveys = Survey.objects.filter(organization=organization).select_related(
            "campaign", "method"
        )

        methods = (
            surveys.values("method__id", "method__name")
            .distinct()
            .order_by("method__name")
        )
        context["methods"] = methods

        campaigns = Campaign.objects.filter(
            survey__organization=organization
        ).distinct()

        table_rows = []
        for campaign in campaigns:
            row = {"campaign": campaign, "cells": []}
            for method in methods:
                survey = next(
                    (
                        s
                        for s in surveys
                        if s.campaign_id == campaign.id
                        and s.method_id == method["method__id"]
                    ),
                    None,
                )
                row["cells"].append(survey)
            table_rows.append(row)

        context["table_rows"] = table_rows
        return context


class ResourcesView(TemplateView):
    template_name = "info/resources.html"


class ContactView(TemplateView):
    template_name = "info/contact.html"
