from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from .forms import get_dynamic_form
from .models import Campaign, Indicator, IndicatorResult, Method, Survey


class MethodFillView(TemplateView):
    template_name = "methods/method_fill.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_method = Method.objects.get(pk=self.kwargs["id"])
        campaign = Campaign.objects.get(methods__id__contains=current_method.id)
        readonly = False
        # Get the current survey already started
        try:
            survey = Survey.objects.get(
                campaign=campaign,
                method=current_method,
                user=self.request.user,
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
    def post(self, request, id):
        action = request.POST.get("action")

        if action == "submit":
            form = forms.Form(request.POST)
            if not form.is_valid():
                pass

        current_method = Method.objects.get(pk=self.kwargs["id"])
        try:
            campaign = Campaign.objects.get(methods__id__contains=current_method.id)
        except ObjectDoesNotExist as error:
            raise ObjectDoesNotExist(
                _("The method has no asociated campaign and can't be answered")
            ) from error

        if campaign is not None:
            survey, created = Survey.objects.get_or_create(
                method=current_method,
                user=request.user,
                campaign=campaign,
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

            return redirect("/")
