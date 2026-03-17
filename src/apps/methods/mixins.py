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
from .models import (
    Campaign,
    Group,
    Indicator,
    IndicatorResult,
    List,
    Method,
    Section,
    Survey,
)


class MethodFillMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # External survey
        if not is_valid_uuid(self.request.user.id):
            method_fill_context = prepare_method_fill_context(
                None, None, None, None, kwargs.get("token"), self.request
            )
        # Method
        else:
            method_fill_context = prepare_method_fill_context(
                None,
                kwargs.get("method"),
                kwargs.get("campaign_id"),
                self.request.user,
                None,
                self.request,
            )

        context.update(method_fill_context)
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


def prepare_method_fill_context(
    survey_id=None, method=None, campaign_id=None, user=None, token=None, request=None
):
    # Get the current survey already started
    try:
        if survey_id is not None:
            survey = Survey.objects.get(pk=survey_id)
        elif token is not None:  # External survey
            survey = Survey.objects.get(
                token=token,
                campaign__id=campaign_id,
                method=method,
            )
        else:
            survey = Survey.objects.get(
                user=user,
                campaign__id=campaign_id,
                method=method,
            )

        readonly = survey.status == Survey.Status.CLOSED
        placeholder_dict = get_previous_campaign_answers(
            survey.campaign.id, survey.method.id, survey.user
        )
        campaign_id = survey.campaign.id
        method = survey.method
        user = survey.user
        form = get_dynamic_form(
            survey.method,
            IndicatorResult.objects.filter(survey=survey),
            readonly,
            placeholder_dict,
        )

    except ObjectDoesNotExist:
        # If there is none, get new survey
        readonly = False
        placeholder_dict = get_previous_campaign_answers(campaign_id, method.id, user)
        form = get_dynamic_form(method, [], False, placeholder_dict)

    sections = get_sections(method, form(data=request.POST or None))

    try:
        indicators = list(Method.objects.get(id=method.id).indicators.all().values())
        for i in indicators:
            i["unit"] = Indicator.Unit(i["unit"]).label if i["unit"] else ""
            # Add options value
            if i["list_options_id"] is not None:
                list_options = List.objects.get(id=i["list_options_id"])
                options = list_options.items.all().values()
                i["options"] = []
                for o in options:
                    i["options"].append({"id": o["id"], "value": o["value"]})
            # Add group data
            if i["group_id"] is not None:
                group = Group.objects.get(id=i["group_id"])
                group_items = group.items.all().values()
                i["group_title"] = group.title
                i["group_items"] = []
                for o in group_items:
                    i["group_items"].append(
                        {"id": o["id"], "title": o["title"], "suffix": o["suffix"]}
                    )
            # Add group_2 data
            if i["group_2_id"] is not None:
                group = Group.objects.get(id=i["group_2_id"])
                group_items = group.items.all().values()
                i["group_2_title"] = group.title
                i["group_2_items"] = []
                for o in group_items:
                    i["group_2_items"].append(
                        {"id": o["id"], "title": o["title"], "suffix": o["suffix"]}
                    )

    except Method.DoesNotExist:
        indicators = list([])

    return {
        "method_name": method.name,
        "campaign_id": campaign_id,
        "readonly": readonly,
        "form": form,
        "sections": sections,
        "sections_data": get_sections_data(method),
        "indicators": indicators,
        "initial_values": get_initial_values(survey) if "survey" in locals() else {},
        "placeholders": placeholder_dict,
    }


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
        # Handle group indicators
        elif indicator.is_group_indicator:
            for group_item in indicator.group.items.all():
                # Handle lists
                if indicator.group_2 is None:
                    value = request.POST.get(f"{field_name}_{group_item.suffix}")
                    if value or na:
                        IndicatorResult.objects.update_or_create(
                            survey=survey,
                            indicator=indicator,
                            group_item=group_item,
                            defaults={
                                "value": "" if value is None else value,
                                "not_applicable": na,
                            },
                        )
                    else:
                        IndicatorResult.objects.filter(
                            survey=survey,
                            indicator=indicator,
                            group_item=group_item,
                        ).delete()
                # Handle tables
                else:
                    for group_2_item in indicator.group_2.items.all():
                        value = request.POST.get(
                            f"{field_name}_{group_item.suffix}_{group_2_item.suffix}"
                        )
                        if value or na:
                            IndicatorResult.objects.update_or_create(
                                survey=survey,
                                indicator=indicator,
                                group_item=group_item,
                                group_2_item=group_2_item,
                                defaults={
                                    "value": "" if value is None else value,
                                    "not_applicable": na,
                                },
                            )
                        else:
                            IndicatorResult.objects.filter(
                                survey=survey,
                                indicator=indicator,
                                group_item=group_item,
                                group_2_item=group_2_item,
                            ).delete()
                    # Save group totals
                    value = request.POST.get(f"{field_name}_{group_item.suffix}_total")
                    IndicatorResult.objects.update_or_create(
                        survey=survey,
                        indicator=indicator,
                        group_item=group_item,
                        group_2_item=None,
                        is_total=True,
                        defaults={
                            "value": "" if value is None else value,
                            "not_applicable": na,
                        },
                    )
            if indicator_is_numeric(indicator.data_type):
                # Save group2 totals
                if indicator.group_2 is not None:
                    for group_2_item in indicator.group_2.items.all():
                        value = request.POST.get(
                            f"{field_name}_{group_2_item.suffix}_total"
                        )
                        IndicatorResult.objects.update_or_create(
                            survey=survey,
                            indicator=indicator,
                            group_item=None,
                            group_2_item=group_2_item,
                            is_total=True,
                            defaults={
                                "value": "" if value is None else value,
                                "not_applicable": na,
                            },
                        )
                # Save total
                value = request.POST.get(f"{field_name}_total")
                IndicatorResult.objects.update_or_create(
                    survey=survey,
                    indicator=indicator,
                    group_item=None,
                    group_2_item=None,
                    is_total=True,
                    defaults={
                        "value": "" if value is None else value,
                        "not_applicable": na,
                    },
                )
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
    # On previews there is no campaign
    if campaign_id:
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
                        code = r.indicator.code
                        if r.gender is not None:
                            placeholder_dict[code][get_gender_suffix(r.gender)] = (
                                r.value
                            )
                        elif r.group_item is not None and r.group_2_item is not None:
                            if r.group_item.suffix not in placeholder_dict[code]:
                                placeholder_dict[code][r.group_item.suffix] = {}
                            placeholder_dict[code][r.group_item.suffix][
                                r.group_2_item.suffix
                            ] = r.value
                        elif r.group_item is not None and r.group_2_item is None:
                            placeholder_dict[code][r.group_item.suffix] = r.value
                        else:
                            placeholder_dict[code] = r.value

    return placeholder_dict


def get_initial_values(survey):
    indicator_results = IndicatorResult.objects.filter(
        survey=survey,
    ).all()
    initial_values = {}
    for i in indicator_results:
        if i.is_total:
            continue
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
        elif i.indicator.is_group_indicator:
            if i.indicator.group_2 is None:
                if i.indicator.code not in initial_values:
                    initial_values[i.indicator.code] = {
                        "value": {},
                        "not_applicable": i.not_applicable,
                    }
                    initial_values[i.indicator.code]["value"][i.group_item.suffix] = (
                        i.value
                    )
                else:
                    initial_values[i.indicator.code]["value"][i.group_item.suffix] = (
                        i.value
                    )
            else:
                if i.indicator.code not in initial_values:
                    initial_values[i.indicator.code] = {
                        "value": {},
                        "not_applicable": i.not_applicable,
                    }
                    for item in i.indicator.group.items.all():
                        initial_values[i.indicator.code]["value"][item.suffix] = {}
                    initial_values[i.indicator.code]["value"][i.group_item.suffix][
                        i.group_2_item.suffix
                    ] = i.value
                else:
                    initial_values[i.indicator.code]["value"][i.group_item.suffix][
                        i.group_2_item.suffix
                    ] = i.value
        else:
            initial_values[i.indicator.code] = {
                "value": i.value,
                "not_applicable": i.not_applicable,
            }
    return initial_values


def get_sections(current_method, form_instance):
    # Convert field objects array into a dictionary
    field_lookup = {name: form_instance[name] for name in form_instance.fields}
    sections = get_form_sections(current_method)
    # Store fields HTML in indicator object
    for _, section in sections.items():
        # Top‑level indicators
        for indicator in section["indicators"]:
            field_obj = field_lookup[indicator["field_name"]]
            indicator["field"] = field_obj  # or str(field_obj) for raw HTML

        # Subsection indicators
        for subsection in section["subsections"]:
            for _, sub_inds in subsection.items():
                for indicator in sub_inds:
                    field_obj = field_lookup[indicator["field_name"]]
                    indicator["field"] = field_obj

    return sections


def get_sections_data(method):
    sections = Section.objects.filter(method=method).order_by("order")
    sections_data = []
    for section in sections:
        indicators_codes = [i["code"] for i in list(section.indicators.all().values())]

        sections_data.append(
            {
                "id": section.id,
                "title": section.title,
                "description": section.description,
                "indicators_codes": indicators_codes,
                "parent_id": section.parent_id,
            }
        )

    return sections_data


def indicator_is_numeric(data_type):
    return (
        data_type == Indicator.DataType.INTEGER
        or data_type == Indicator.DataType.DECIMAL
    )
