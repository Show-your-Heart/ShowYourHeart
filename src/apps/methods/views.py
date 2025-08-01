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
        context["form"] = get_dynamic_form(Method.objects.get(pk=self.kwargs["id"]))

        return context

    @transaction.atomic
    def post(self, request, id):
        current_method = Method.objects.get(pk=self.kwargs["id"])
        try:
            campaign = Campaign.objects.get(methods__id__contains=current_method.id)
        except ObjectDoesNotExist as error:
            raise ObjectDoesNotExist(
                _("The method has no asociated campaign and can't be answered")
            ) from error

        if campaign is not None:
            survey = Survey.objects.create(
                method=current_method, user=request.user, campaign=campaign
            )
            for key, value in request.POST.items():
                if key.startswith("question"):
                    IndicatorResult.objects.create(
                        survey=survey,
                        indicator=Indicator.objects.get(pk=key[len("question_") :]),
                        value=value,
                    )

            return redirect("/")
