import uuid

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect

from .forms import get_dynamic_form
from .models import Indicator, IndicatorResult, Survey


class CommonContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = kwargs.get("campaign")
        current_method = kwargs.get("method")

        readonly = False
        # Get the current survey already started
        try:
            if not is_valid_uuid(self.request.user.id):
                survey = Survey.objects.get(
                    token=self.kwargs["id"],
                    campaign__id=campaign,
                    method=current_method,
                )
            else:
                survey = Survey.objects.get(
                    user=self.request.user,
                    campaign__id=campaign,
                    method=current_method,
                )

            readonly = survey.status == Survey.Status.SUBMITTED
            context["form"] = get_dynamic_form(
                current_method,
                IndicatorResult.objects.filter(survey=survey),
                readonly,
            )
        except ObjectDoesNotExist:
            # If there is none, get new survey
            context["form"] = get_dynamic_form(current_method, [], False)
        context["method_name"] = current_method.name
        context["readonly"] = readonly

        return context

    @transaction.atomic
    def post(self, request, method_id, campaign_id):
        action = request.POST.get("action")

        if action == "submit":
            form = forms.Form(request.POST)
            if not form.is_valid():
                pass

        if not is_valid_uuid(request.user.id):
            survey, created = Survey.objects.get_or_create(
                method_id=method_id,
                token=self.kwargs["id"],
                campaign_id=campaign_id,
            )
        else:
            survey, created = Survey.objects.get_or_create(
                method_id=method_id,
                user=request.user,
                campaign_id=campaign_id,
            )

        if action == "submit":
            survey.status = Survey.Status.SUBMITTED
            survey.save()

        for key, value in request.POST.items():
            if key.startswith("question"):
                IndicatorResult.objects.update_or_create(
                    survey=survey,
                    indicator=Indicator.objects.get(pk=key[len("question_") :]),
                    defaults={"value": value},
                )

        return HttpResponseRedirect(request.path_info)


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False
