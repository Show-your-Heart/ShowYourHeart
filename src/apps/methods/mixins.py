import uuid
from collections import defaultdict

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils import timezone

from .forms import get_dynamic_form
from .helpers import (
    get_form_sections,
    get_gender_field_value,
    get_gender_suffix,
    is_gendered,
)
from .models import Campaign, Indicator, IndicatorResult, Method, Survey


class MethodFillMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign_id = kwargs.get("campaign")
        current_method = kwargs.get("method")

        placeholder_dict = get_previous_campaign_answers(
            campaign_id, current_method.id, self.request.user
        )

        readonly = False
        # Get the current survey already started
        try:
            if not is_valid_uuid(self.request.user.id):
                survey = Survey.objects.get(
                    token=self.kwargs["id"],
                    campaign__id=campaign_id,
                    method=current_method,
                )
            else:
                survey = Survey.objects.get(
                    user=self.request.user,
                    campaign__id=campaign_id,
                    method=current_method,
                )

            readonly = survey.status == Survey.Status.CLOSED
            form = get_dynamic_form(
                current_method,
                IndicatorResult.objects.filter(survey=survey),
                readonly,
                placeholder_dict,
            )

            context["initial_values"] = get_initial_values(survey)

        except ObjectDoesNotExist:
            # If there is none, get new survey
            form = get_dynamic_form(current_method, [], False, placeholder_dict)

        context["form"] = form
        context["method_name"] = current_method.name
        context["readonly"] = readonly
        context["sections"] = get_sections(
            current_method, form(data=self.request.POST or None)
        )

        context["sections_data"] = get_sections_data(context["sections"])
        try:
            indicators = list(
                Method.objects.get(id=current_method.id).indicators.all().values()
            )
            for i in indicators:
                i["unit"] = Indicator.Unit(i["unit"]).label if i["unit"] else ""

        except Method.DoesNotExist:
            indicators = list([])

        context["indicators"] = indicators
        return context

    @transaction.atomic
    def post(self, request, method_id, campaign_id, project_id=None):
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
                organization=request.user.profile.organization,
                project_id=project_id,
                campaign_id=campaign_id,
            )

        current_date = timezone.now()
        if created:
            survey.start_date = current_date

        if action == "submit":
            survey.status = Survey.Status.CLOSED
            survey.closed_date = current_date

        survey.modified_date = current_date

        if survey.status == Survey.Status.TECH_VALIDATED:
            survey.validated_date = current_date

        if survey.status == Survey.Status.QUALITY_CHECKED:
            survey.evaluated_date = current_date

        survey.save()

        save_indicator_results(method_id, request, survey)

        return HttpResponseRedirect(request.path_info)


def save_indicator_results(method_id, request, survey):
    method = Method.objects.get(pk=method_id)

    for indicator in method.indicators.all():
        field_name = f"question_{indicator.id}"
        na = (
            None
            if not indicator.mandatory
            else request.POST.get(f"{field_name}_na", False)
        )
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
                value = request.POST.get(f"{field_name}_{suffix}")
                if value or na:
                    IndicatorResult.objects.update_or_create(
                        survey=survey,
                        indicator=indicator,
                        gender=gender,
                        defaults={
                            "value": "" if value is None else value,
                            "not_applicable": na,
                        },
                    )
                else:
                    IndicatorResult.objects.filter(
                        survey=survey, indicator=indicator, gender=gender
                    ).delete()

        # Handle standard indicators
        else:
            values = request.POST.getlist(field_name)
            formatted_values = "|".join(values)
            if formatted_values or na:
                IndicatorResult.objects.update_or_create(
                    survey=survey,
                    indicator=indicator,
                    defaults={"value": formatted_values, "not_applicable": na},
                )
            else:
                IndicatorResult.objects.filter(
                    survey=survey, indicator=indicator
                ).delete()


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False


def get_previous_campaign_answers(campaign_id, current_method_id, user):
    placeholder_dict = defaultdict(dict)
    current_campaign = Campaign.objects.get(id=campaign_id)
    if current_campaign.previous_campaign:
        # Check if the method was included on the previous campaign
        previous_campaign = Campaign.objects.filter(
            id=current_campaign.previous_campaign.id,
            methods__id__contains=current_method_id,
        ).first()

        if previous_campaign:
            # Check if the user answered the same method on the previous campaign
            previous_survey = Survey.objects.filter(
                user=user,
                campaign__id=previous_campaign.id,
                method__id=current_method_id,
            ).first()

            if previous_survey:
                indicator_results = IndicatorResult.objects.filter(
                    survey=previous_survey,
                )

                for r in indicator_results:
                    field_name = f"question_{r.indicator.id}"
                    if r.gender is not None:
                        placeholder_dict[field_name][get_gender_suffix(r.gender)] = (
                            r.value
                        )
                    else:
                        placeholder_dict[field_name] = r.value

    return placeholder_dict


def get_initial_values(survey):
    indicator_results = IndicatorResult.objects.filter(
        survey=survey,
    ).all()
    initial_values = {}
    for i in indicator_results:
        if is_gendered(i.indicator.data_type):
            initial_values[i.indicator.code] = {
                "value": {
                    "non_binary": get_gender_field_value(
                        indicator_results, i.indicator, "non_binary"
                    ),
                    "male": get_gender_field_value(
                        indicator_results, i.indicator, "male"
                    ),
                    "female": get_gender_field_value(
                        indicator_results, i.indicator, "female"
                    ),
                },
                "not_applicable": i.not_applicable,
            }
        else:
            initial_values[i.indicator.code] = {
                "value": i.value,
                "not_applicable": i.not_applicable,
            }
    return initial_values


def get_sections(current_method, form_instance):
    field_lookup = {name: form_instance[name] for name in form_instance.fields}
    sections = get_form_sections(current_method)
    for _, sec_val in sections.items():
        # ---- top‑level indicators ----
        enriched_top = []
        for ind in sec_val["indicators"]:
            # ind is like {"field_name": "question_42", "indicator": <Indicator …>}
            field_obj = field_lookup.get(ind["field_name"])
            # Attach the bound field (or its HTML) directly:
            ind["field"] = field_obj  # or str(field_obj) for raw HTML
            enriched_top.append(ind)
        sec_val["indicators"] = enriched_top

        # ---- subsections ----
        for sub_dict in sec_val[
            "subsections"
        ]:  # each sub_dict is {title: [indicators]}
            for sub_title, sub_inds in sub_dict.items():
                enriched_sub = []
                for ind in sub_inds:
                    field_obj = field_lookup.get(ind["field_name"])
                    ind["field"] = field_obj
                    enriched_sub.append(ind)
                sub_dict[sub_title] = enriched_sub

    return sections


def get_sections_data(context_sections):
    sections_data = []
    for section in context_sections:
        sections_data.append(
            {
                "id": section.id,
                "title": section.title,
                "indicators_ids": [
                    i["id"] for i in list(section.indicators.all().values())
                ],
            }
        )
    return sections_data
