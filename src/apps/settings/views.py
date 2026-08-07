from django.utils.translation import get_language
from django.views.generic import TemplateView

from apps.methods.models import Campaign, Survey


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

        survey_names = sorted({s.method.name for s in surveys})
        context["survey_names"] = survey_names

        campaigns = Campaign.objects.filter(
            survey__organization=organization
        ).distinct()

        table_rows = []
        for campaign in campaigns:
            row = {
                "campaign": campaign,
                "cells": [],
                "has_evaluated": False,
            }
            for name in survey_names:
                survey = None
                for s in surveys:
                    if s.campaign_id == campaign.id and s.method.name == name:
                        survey = s
                        if survey.evaluated_date:
                            row["has_evaluated"] = True
                        if survey.validated_date:
                            row["has_validated"] = True

                row["cells"].append(survey)
            table_rows.append(row)

        context["table_rows"] = table_rows
        context["language"] = get_language()
        return context


class ResourcesView(TemplateView):
    template_name = "info/resources.html"


class ContactView(TemplateView):
    template_name = "info/contact.html"
