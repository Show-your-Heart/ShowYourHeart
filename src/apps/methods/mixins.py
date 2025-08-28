import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect

from .forms import get_dynamic_form, get_form_sections
from .models import Indicator, IndicatorResult, Method, Survey


class MethodFillMixin:
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
        context["sections"] = get_form_sections(current_method)

        return context

    @transaction.atomic
    def post(self, request, method_id, campaign_id):
        action = request.POST.get("action")

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
                organization_id=request.user.profile.organization.id,
            )

        if action == "submit":
            survey.status = Survey.Status.SUBMITTED
            survey.save()

        method = Method.objects.get(pk=method_id)

        for indicator in method.indicators.all():
            field_name = f"question_{indicator.id}"

            # Handle gendered indicators
            if indicator.data_type in [
                Indicator.DataType.INTEGERGENDER,
                Indicator.DataType.DECIMALGENDER,
            ]:
                for suffix, gender in {
                    "male": IndicatorResult.Gender.MALE,
                    "female": IndicatorResult.Gender.FEMALE,
                    "non_binary": IndicatorResult.Gender.NON_BINARY,
                }.items():
                    values = request.POST.getlist(f"{field_name}_{suffix}")
                    if values:
                        IndicatorResult.objects.update_or_create(
                            survey=survey,
                            indicator=indicator,
                            gender=gender,
                            defaults={"value": "|".join(values)},
                        )

            # Handle normal indicators
            else:
                values = request.POST.getlist(field_name)
                if values:
                    IndicatorResult.objects.update_or_create(
                        survey=survey,
                        indicator=indicator,
                        defaults={"value": "|".join(values)},
                    )

        return HttpResponseRedirect(request.path_info)


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False
